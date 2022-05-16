"""
This module contains code to find starting point on each main stream.
"""

from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from typing import Callable, Generator, List, Optional, Tuple, Union

import fiona
import geosardine as dine
import numpy as np
import rasterio
import whitebox
from rasterio.features import geometry_mask
from shapely import geometry, ops, speedups
from shapely.geometry import Point
from shapely.geometry.base import BaseGeometry
from tqdm.autonotebook import tqdm

from .custom_types import GeoJsonDict

speedups.disable()

wbt = whitebox.WhiteboxTools()


class StemTooShort(Exception):
    """Stream/Stem is too short to calculate volume. It is near the start vertex"""

    pass


class DifferentCRS(Exception):
    """two data have different CRS"""

    pass


class ProcessingData:
    """
    Contains processing data in temporary directory
    """

    def __init__(self, flow_direction: Path, flow_stream: Path) -> None:
        self.temp_folder = TemporaryDirectory()
        self.temp_path = Path(self.temp_folder.name)
        self.flow_direction = flow_direction
        self.flow_stream = flow_stream

        self.main_stem_rasterfile = self.temp_path / "main_stem.tif"
        self.main_stem_vectorfile = self.temp_path / "main_stem.shp"
        self.link_class_file = self.temp_path / "link_class.tif"

        self.link_class: Optional["dine.Raster"] = None

        self.generate()

    def generate(self) -> None:
        """generate processing data"""
        wbt.find_main_stem(
            self.flow_direction,
            self.flow_stream,
            self.main_stem_rasterfile,
            esri_pntr=True,
        )
        wbt.stream_link_class(
            self.flow_direction, self.flow_stream, self.link_class_file, esri_pntr=True
        )
        wbt.raster_streams_to_vector(
            self.main_stem_rasterfile,
            self.flow_direction,
            self.main_stem_vectorfile,
            esri_pntr=True,
        )

        self.link_class = dine.Raster.from_rasterfile(str(self.link_class_file))
        print("processing data has been generated")

    def save(self, output_directory: Path) -> None:
        """Copy processing data to outside temporary directory

        Parameters
        ----------
        output_directory : Path
            directory to copy processing data
        """
        for f in self.temp_path.glob("*"):
            if f.is_file():
                copy2(f.absolute(), output_directory)

    def cleanup(self) -> None:
        """remove  temporary directory"""
        self.temp_folder.cleanup()


def interpolate_points(
    polyline: geometry.LineString, distance: float = 0.25, upstream: int = 0
) -> Generator[geometry.Point, None, None]:
    """interpolate points along line

    Parameters
    ----------
    polyline : geometry.LineString
        stream
    distance : float, optional
        interpolation distance, by default 0.25
    upstream : int, optional
        [description], by default 0

    Yields
    -------
    Generator[geometry.Point, None, None]
        interpolated points
    """
    interpolate_distances = np.arange((polyline.length // distance) + 1)
    for interpolate_distance in interpolate_distances:
        yield polyline.interpolate(interpolate_distance)


def estimate_volume(array: np.ndarray, dsm_diff: dine.Raster) -> float:
    """estimate volume

    Parameters
    ----------
    array : np.ndarray
        clipped dsm difference of 2 epoch by buffered starting point
    dsm_diff : dine.Raster
        dsm difference of 2 epoch

    Returns
    -------
    float
        volume
    """
    return float(
        np.sum(array[(array > dsm_diff.no_data) & (array > 0)]) * dsm_diff.resolution[0]
    )


def calculate_volume_stem(
    stem: geometry.LineString,
    point: geometry.Point,
    dsm_diff: "dine.Raster",
    stream_buffer_size: float,
) -> float:
    """Calculate stem by buffering the stem

    Parameters
    ----------
    stem : geometry.LineString
        stream
    point : geometry.Point
        starting point
    dsm_diff : dine.Raster
        dsm difference of 2 epoch
    stream_buffer_size : float
        buffer length for stream

    Returns
    -------
    float
        volume

    Raises
    ------
    StemTooShort
        stem is below 5 times spatial resolution which will caused too small volume
    """
    splitted = ops.split(stem, point.buffer(0.1))
    if splitted[0].length < dsm_diff.resolution[0] * 5:
        raise StemTooShort
    mask = geometry_mask(
        [geometry.mapping(splitted[0].buffer(stream_buffer_size))],
        transform=dsm_diff.transform,
        out_shape=dsm_diff.shape[:2],
    )
    return float(
        (
            dsm_diff.array[
                (~mask.reshape(mask.shape[0], mask.shape[1], 1))
                & (dsm_diff > 0)
                & (dsm_diff != dsm_diff.no_data)
            ]
            * dsm_diff.resolution[0]
        ).sum()
    )


def find_starting_point(
    stem: geometry.LineString,
    distance: float,
    dsm_diff: "dine.Raster",
    link_class: "dine.Raster",
    stream_buffer_size: float,
) -> Tuple[Optional[geometry.Point], Optional[float]]:
    """find starting point over main stem

    Parameters
    ----------
    stem : geometry.LineString
        main stem
    distance : float
        interpolation distance
    dsm_diff : dine.Raster
        dsm difference of 2 epoch
    link_class : dine.Raster
        stream link class
    stream_buffer_size : float
        buffer length for stream

    Returns
    -------
    Tuple[Optional[geometry.Point], Optional[float]]
        Starting point and volume
        if geometry.Point & float, there is starting point
        if None & None, there isn't any starting point

    Raises
    ------
    ValueError
        Wrong type
    """

    if stem.length < 100:
        return None, None

    buffer_pixel = 5
    buffer_area = (buffer_pixel * 2) ** 2
    minimum_pixel = buffer_area * 0.5

    point_in_stem = interpolate_points(stem, distance)

    sp_candidates: List[geometry.Point] = []
    sp_candidates_junction: List[geometry.Point] = []
    for point in point_in_stem:
        point_diff = dsm_diff.xy_value(point.x, point.y)
        if point_diff != dsm_diff.no_data and point_diff >= 0:
            row, col = dsm_diff.xy2rowcol(point.x, point.y)

            bounding_box = np.array(
                [
                    row - buffer_pixel,
                    col - buffer_pixel,
                    row + buffer_pixel,
                    col + buffer_pixel,
                ]
            )

            deposition_pixel_count: int = np.sum(
                dsm_diff.array[
                    bounding_box[0] : bounding_box[2], bounding_box[1] : bounding_box[3]
                ]
                > 0
            )

            if (
                np.all(bounding_box > 0)
                and dsm_diff.array[row, col] > 0
                and deposition_pixel_count > minimum_pixel
            ):
                link_type = link_class.xy_value(point.x, point.y)

                if not isinstance(link_type, np.ndarray):
                    raise ValueError("Unexpected")

                if link_type[0] == 4:
                    sp_candidates_junction.append(point)
                else:
                    sp_candidates.append(point)
    starting_point = None
    if sp_candidates_junction:
        starting_point = sp_candidates_junction[-1]
    elif sp_candidates:
        starting_point = sp_candidates[-1]

    if starting_point is not None:
        try:
            volume: Optional[float] = calculate_volume_stem(
                stem, starting_point, dsm_diff, stream_buffer_size
            )
        except StemTooShort:
            row, col = dsm_diff.xy2rowcol(starting_point.x, starting_point.y)

            bounding_box = np.array(
                [
                    row - buffer_pixel,
                    col - buffer_pixel,
                    row + buffer_pixel,
                    col + buffer_pixel,
                ]
            )

            buffered_point = dsm_diff.array[
                bounding_box[0] : bounding_box[2], bounding_box[1] : bounding_box[3]
            ]
            volume = estimate_volume(
                buffered_point[buffered_point != dsm_diff.no_data],
                dsm_diff,
            )
    else:
        volume = None

    return starting_point, volume


def find_starting_points(
    input_earlier_dsm: str,
    input_later_dsm: str,
    input_flow_direction: str,
    input_flow_stream: str,
    max_percent_length: float,
    stream_buffer_size: float,
    return_processing_data: bool = False,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> Tuple[List[Tuple[Point, float]], Optional[ProcessingData]]:
    """Batch find starting point for streams

    Parameters
    ----------
    input_earlier_dsm : str
        earlier dsm (first epoch) location
    input_later_dsm : str
        later dsm (second epoch) location
    input_flow_direction : str
        flow direction location d8-esri-style
    input_flow_stream : str
        flow stream location
    max_percent_length : float
        maximum percentage of stream to be included
    stream_buffer_size : float
        buffer length for stream
    return_processing_data : bool, optional
        return processing data as variable, by default False
    progress_callback : Optional[Callable[[int, int], None]], optional
        callback to be called after each loop, by default None

    Returns
    -------
    Tuple[List[Tuple[Point, float]], Optional[ProcessingData]]
        starting point, volume & processing data
        if Tuple[List[Tuple[Point, float]], ProcessingData], processing data is returned
        if Tuple[List[Tuple[Point, float]], None], processing data is not returned

    Raises
    ------
    ValueError
        Different CRS
    ValueError
        Wrong type
    e
        There is any exception raised
    """
    if progress_callback is not None:
        progress_callback(0, 0)

    processing_data = ProcessingData(
        Path(input_flow_direction), Path(input_flow_stream)
    )

    try:
        print(processing_data.main_stem_vectorfile)
        print("r", input_earlier_dsm, input_later_dsm)
        with fiona.open(processing_data.main_stem_vectorfile) as lines, rasterio.open(
            input_earlier_dsm
        ) as earlier_dsm, rasterio.open(input_later_dsm) as later_dsm:
            earlier_dsm = dine.Raster.from_rasterfile(input_earlier_dsm)
            later_dsm = dine.Raster.from_rasterfile(input_later_dsm)

            if later_dsm.epsg != earlier_dsm.epsg:
                raise ValueError("Both dsm should be in the same reference system")

            dsm_diff = later_dsm - earlier_dsm

            starting_points: List[Tuple[Point, float]] = []
            sp_coordinates: np.ndarray = np.empty((1, 2), dtype=np.float32)

            features: Tuple[Tuple[int, GeoJsonDict], ...] = tuple(
                lines.items(
                    bbox=(
                        later_dsm.x_min,
                        later_dsm.y_min,
                        later_dsm.x_max,
                        later_dsm.y_max,
                    )
                )
            )

            progress_total = len(features)

            for i, feature in tqdm(features, total=progress_total):

                line = feature["geometry"]["coordinates"]
                if later_dsm.xy_value(
                    *feature["geometry"]["coordinates"][0]
                ) < later_dsm.xy_value(*feature["geometry"]["coordinates"][-1]):
                    line = feature["geometry"]["coordinates"][::-1]

                stem = geometry.LineString(line)
                stem = ops.substring(stem, 0, stem.length * max_percent_length / 100)

                # if isinstance(stem, BaseGeometry) or processing_data.link_class is None:
                #     raise ValueError("Unexpected")

                starting_point, volume = find_starting_point(
                    stem, 0.25, dsm_diff, processing_data.link_class, stream_buffer_size
                )
                if starting_point is not None and volume is not None:
                    near_sp_exist = any(
                        (
                            np.abs(sp_coordinates[:, 0] - starting_point.x)
                            + np.abs(sp_coordinates[:, 1] - starting_point.y)
                        )
                        <= 3
                    )

                    if not near_sp_exist:
                        starting_points.append((starting_point, volume))

                if progress_callback is not None:
                    progress_callback(progress_total, i + 1)
            if return_processing_data:
                return starting_points, processing_data
            else:
                # processing_data.cleanup()
                return starting_points, None
    except Exception as e:
        processing_data.cleanup()
        raise e


def save2txt(
    starting_points: List[Tuple[Point, float]], output_location: Union[Path, str]
) -> None:
    """Save starting points and volume as csv

    Parameters
    ----------
    starting_points : List[Tuple[Point, float]]
        list of starting point as Point and volume
    output_location : Union[Path, str]
        location to save starting point
    """
    with open(output_location, "w") as out:
        for starting_point, volume in starting_points:
            out.writelines(f"{starting_point.x},{starting_point.y},{volume}\n")
