import os
from dataclasses import dataclass
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import fiona
import geosardine as dine
import numpy as np
import rasterio
import shapely
import whitebox
from rasterio import Affine
from rasterio.features import geometry_mask
from shapely import geometry, ops, speedups
from shapely.geometry import LineString, Point
from tqdm.autonotebook import tqdm

from pearpy.starting_point import find_starting_point

from .custom_types import GeoJsonDict

speedups.disable()

wbt = whitebox.WhiteboxTools()


class StemTooShort(Exception):
    pass


class ProcessingData:
    def __init__(self, flow_direction, flow_stream):
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
        # self.link_class.save(str(output_directory / "link_class.tif"))
        for f in self.temp_path.glob("*"):
            if f.is_file():
                copy2(f.absolute(), output_directory)

    def cleanup(self) -> None:
        self.temp_folder.cleanup()


def interpolate_points(
    polyline: geometry.LineString, distance: float = 0.25, upstream: int = 0
) -> Generator[geometry.Point, None, None]:
    interpolate_distances = np.arange(polyline.length // distance) * distance
    interpolate_distances = np.append(interpolate_distances, polyline.length)
    for interpolate_distance in interpolate_distances:
        yield polyline.interpolate(interpolate_distance)


def estimate_volume(array: np.ndarray, dsm_diff: dine.Raster) -> float:
    return float(
        np.sum(array[(array > dsm_diff.no_data) & (array > 0)]) * dsm_diff.resolution[0]
    )


def calculate_volume_stem(
    stem: geometry.LineString,
    point: geometry.Point,
    dsm_diff: "dine.Raster",
    stream_buffer_size: float,
) -> float:
    splited = ops.split(stem, point.buffer(0.1))
    if splited[0].length < dsm_diff.resolution[0] * 5:
        raise StemTooShort
    mask = geometry_mask(
        [geometry.mapping(splited[0].buffer(stream_buffer_size))],
        transform=dsm_diff.transform,
        out_shape=dsm_diff.shape[:2],
    )
    return (
        dsm_diff.array[
            (~mask.reshape(mask.shape[0], mask.shape[1], 1))
            & (dsm_diff > 0)
            & (dsm_diff != dsm_diff.no_data)
        ]
        * dsm_diff.resolution[0]
    ).sum()


def find_starting_point(
    stem: geometry.LineString,
    ditance: float,
    dsm_diff: "dine.Raster",
    link_class: "dine.Raster",
    stream_buffer_size: float,
) -> Tuple[Optional[geometry.Point], Optional[float]]:

    if stem.length < 100:
        return None, None

    buffer_pixel = 5
    buffer_area = (buffer_pixel * 2) ** 2
    minimum_pixel = buffer_area * 0.5

    point_in_stem = interpolate_points(stem, ditance)

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

            if np.all(bounding_box > 0) and dsm_diff.array[row, col] > 0:
                buffered_point = dsm_diff.array[
                    bounding_box[0] : bounding_box[2], bounding_box[1] : bounding_box[3]
                ]
                deposition_pixel_count: int = (buffered_point > 0).sum()
                if deposition_pixel_count > minimum_pixel:
                    if link_class.xy_value(point.x, point.y)[0] == 4:
                        sp_candidates_junction.append(point)
                    else:
                        sp_candidates.append(point)

    if len(sp_candidates_junction) > 0:
        starting_point = sp_candidates_junction[-1]
    elif len(sp_candidates) > 0:
        starting_point = sp_candidates[-1]
    else:
        starting_point = None

    if starting_point is not None:
        try:
            volume = calculate_volume_stem(
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
    if progress_callback is not None:
        progress_callback(0, 0)
    processing_data = ProcessingData(input_flow_direction, input_flow_stream)

    try:
        print(processing_data.main_stem_vectorfile)
        print("r",input_earlier_dsm, input_later_dsm)
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

            for i, feature in tqdm(features, total=len(features)):

                line = feature["geometry"]["coordinates"]
                if later_dsm.xy_value(
                    *feature["geometry"]["coordinates"][0]
                ) < later_dsm.xy_value(*feature["geometry"]["coordinates"][-1]):
                    line = feature["geometry"]["coordinates"][::-1]

                stem = geometry.LineString(line)
                stem = ops.substring(stem, 0, stem.length * max_percent_length / 100)

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
    with open(output_location, "w") as out:
        for starting_point, volume in starting_points:
            out.writelines(f"{starting_point.x},{starting_point.y},{volume}\n")
