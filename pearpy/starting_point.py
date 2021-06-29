from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import fiona
import geosardine as dine
import numpy as np
import rasterio
from rasterio import Affine
from shapely import geometry, speedups
from shapely.geometry import LineString, Point
from tqdm.autonotebook import tqdm

from .custom_types import GeoJsonDict

speedups.disable()


def interpolate_points(
    polyline: geometry.LineString, distance: float = 0.25, upstream: int = 0
) -> Generator[geometry.Point, None, None]:
    interpolate_distances = np.arange(polyline.length // distance) * distance
    interpolate_distances = np.append(interpolate_distances, polyline.length)
    if upstream == -1:
        interpolate_distances = interpolate_distances[::-1]
    for interpolate_distance in interpolate_distances:
        yield polyline.interpolate(interpolate_distance)


def get_vertices(
    features: Tuple[Tuple[int, GeoJsonDict], ...],
) -> Generator[Union[Tuple[float, float, float], Tuple[float, float]], None, None]:
    for _, feature in features:
        yield feature["geometry"]["coordinates"][0]
        yield feature["geometry"]["coordinates"][-1]


def estimate_volume(array: np.ndarray, dsm_diff: dine.Raster) -> float:
    return float(np.sum(array[array > dsm_diff.no_data]) * dsm_diff.resolution[0])


def find_starting_point_in_line(
    line: LineString, upstream_index: int, dsm_diff: dine.Raster
) -> Tuple[Optional[geometry.Point], Optional[float]]:
    interpolated = interpolate_points(line, upstream=upstream_index)
    buffer_pixel = 5
    buffer_area = (buffer_pixel * 2) ** 2
    minimum_pixel = buffer_area * 0.7
    candidate_points: List[Tuple[Point, float]] = []

    for point in interpolated:
        try:
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
                deposition_pixel_count = (buffered_point > 0).sum()
                if deposition_pixel_count > minimum_pixel:
                    volume = estimate_volume(
                        buffered_point[buffered_point != dsm_diff.no_data], dsm_diff
                    )
                    candidate_points.append((point, volume))
        except IndexError:
            continue
    if len(candidate_points) == 0:
        return None, None
    else:
        return candidate_points[-1]


def find_upstream(
    feature: GeoJsonDict,
    vertices: np.ndarray,
    dsm: dine.Raster,
    dsm_diff: dine.Raster,
) -> Optional[int]:
    vertices_diff_first = vertices - feature["geometry"]["coordinates"][0]
    vertices_diff_last = vertices - feature["geometry"]["coordinates"][-1]

    distance_to_first = np.abs(vertices_diff_first[:, 0]) + np.abs(
        vertices_diff_first[:, 1]
    )
    distance_to_last = np.abs(vertices_diff_last[:, 0]) + np.abs(
        vertices_diff_last[:, 1]
    )

    nearest_point_first = len(distance_to_first[distance_to_first == 0])
    nearest_point_last = len(distance_to_last[distance_to_last == 0])

    if nearest_point_last == 1 or nearest_point_first == 1:
        upstream_index = 0
        downstream_index = -1
        if nearest_point_last == 1:
            upstream_index = -1
            downstream_index = 0

        # z_upstream = dine.drape2raster(
        #     list(feature["geometry"]["coordinates"][upstream_index]),
        #     dsm.array,
        #     dsm.affine,
        # )[2]
        # z_downstream = dine.drape2raster(
        #     list(feature["geometry"]["coordinates"][downstream_index]),
        #     dsm.array,
        #     dsm.affine,
        # )[2]
        try:
            z_upstream = dsm.xy_value(
                *feature["geometry"]["coordinates"][upstream_index]
            )
            z_downstream = dsm.xy_value(
                *feature["geometry"]["coordinates"][downstream_index]
            )

            if z_upstream > z_downstream and z_upstream != dsm.no_data:
                deposit_upstream = dsm_diff.xy_value(
                    *feature["geometry"]["coordinates"][upstream_index]
                )
                deposit_downstream = dsm_diff.xy_value(
                    *feature["geometry"]["coordinates"][downstream_index]
                )

                if (
                    deposit_upstream != dsm_diff.no_data
                    and deposit_downstream != dsm_diff.no_data
                ):
                    return upstream_index
        except IndexError:
            print("skipped")
            pass

    return None


def find_starting_point(
    feature: Dict[Any, Any],
    vertices: np.ndarray,
    dsm: dine.Raster,
    dsm_diff: dine.Raster,
) -> Tuple[Optional[geometry.Point], Optional[float]]:
    _feature = GeoJsonDict(
        type=feature["type"],
        id=feature["id"],
        properties=feature["properties"],
        geometry=feature["geometry"],
    )

    if geometry.shape(_feature["geometry"]).length < 5.0:
        """Filter by length"""
        return None, None

    upstream_index = find_upstream(_feature, vertices, dsm, dsm_diff)
    if upstream_index is not None:
        starting_point, volume = find_starting_point_in_line(
            geometry.LineString(_feature["geometry"]["coordinates"]),
            upstream_index,
            dsm_diff,
        )

        return starting_point, volume
    return None, None


def find_starting_points(
    input_stream_vector: str,
    input_earlier_dsm: str,
    input_later_dsm: str,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[Tuple[Point, float]]:
    with fiona.open(input_stream_vector) as lines, rasterio.open(
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

        vertices = np.array(list(get_vertices(features)))
        progress_total = len(features)

        for i, feature in tqdm(features, total=len(features)):
            starting_point, volume = find_starting_point(
                feature, vertices, later_dsm, dsm_diff
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
        return starting_points


def save2txt(
    starting_points: List[Tuple[Point, float]], output_location: Union[Path, str]
) -> None:
    with open(output_location, "w") as out:
        for starting_point, volume in starting_points:
            out.writelines(f"{starting_point.x},{starting_point.y},{volume}\n")
