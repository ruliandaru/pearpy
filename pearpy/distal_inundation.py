from collections import OrderedDict
from dataclasses import dataclass, field
from math import log10, sqrt
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import fiona
import numpy as np
import rasterio
from geosardine.raster import polygonize
from tqdm.autonotebook import tqdm

from pearpy.custom_types import RasterioMeta

from .textfile import py_xxplanb, py_xxsecta, py_xxttabl


def text2list(file_name: str) -> List[List[float]]:
    """Parse coordinate and volume into list

    Parameters
    ----------
    file_name : str
        coordinate and volume file

    Returns
    -------
    List[List[float]]
        [[coordinate_x, coordinate_y, volume]]
    """
    with open(file_name) as input_file:
        dataset: List[List[float]] = [
            [round(float(coordinate)) for coordinate in line.split(",")]
            for line in input_file
            if "," in line
        ]

    return sorted(dataset)


cardinal_first = {32: (16, 64), 128: (64, 1), 2: (1, 4), 8: (4, 16)}
cardinal_second = {1: (128, 2), 4: (2, 8), 16: (8, 32), 64: (32, 128)}

checker_board: Dict[int, Callable[[int, int], Tuple[int, int]]] = {
    8: lambda r, c: (r + 1, c),
    32: lambda r, c: (r, c - 1),
    128: lambda r, c: (r - 1, c),
    2: lambda r, c: (r, c + 1),
}

confidence2index = {
    "50.0": 1,
    "70.0": 2,
    "80.0": 3,
    "90.0": 4,
    "95.0": 5,
    "97.5": 6,
    "99.0": 7,
}

left_cell: Dict[int, Callable[[int, int], Tuple[int, int]]] = {
    1: lambda r, c: (r - 1, c),
    2: lambda r, c: (r - 1, c + 1),
    4: lambda r, c: (r, c + 1),
    8: lambda r, c: (r + 1, c + 1),
    16: lambda r, c: (r + 1, c),
    32: lambda r, c: (r + 1, c - 1),
    64: lambda r, c: (r, c - 1),
    128: lambda r, c: (r - 1, c - 1),
}

move_downstream: Dict[int, Callable[[int, int], Tuple[int, int]]] = {
    1: lambda r, c: (r, c + 1),
    2: lambda r, c: (r + 1, c + 1),
    4: lambda r, c: (r + 1, c),
    8: lambda r, c: (r + 1, c - 1),
    16: lambda r, c: (r, c - 1),
    32: lambda r, c: (r - 1, c - 1),
    64: lambda r, c: (r - 1, c),
    128: lambda r, c: (r - 1, c + 1),
}

next_cell: Dict[int, Tuple[int, int]] = {
    1: (-1, 0),
    2: (-1, 1),
    4: (0, 1),
    8: (1, 1),
    16: (1, 0),
    32: (1, -1),
    64: (0, -1),
    128: (-1, -1),
}


class CrossSectionTooLong(Exception):
    """Exception called if volume is too big which caused the cross section too long.

    Parameters
    ----------
    Exception : [type]
        [description]
    """
    pass


@dataclass
class DEMData:
    array: np.ndarray
    cell_diagonal: float
    cell_width: float


@dataclass
class PlanimetricData:
    """Planimetric area information and function
    """
    value: List[float]
    array: np.ndarray
    cross_area: List[float]
    cross_area_ori: List[float] = field(default_factory=list)
    previous_count: int = 0
    last_count: int = 0

    def __post_init__(self) -> None:
        """create a copy of original to reset the data after move downward
        """
        self.cross_area_ori = self.cross_area.copy()

    def restore(self) -> None:
        """reset the data after move downward
        """
        self.cross_area = self.cross_area_ori.copy()

    def pop_cross(self) -> None:
        """pop cross area"""
        self.cross_area.pop()
        self.cross_area_ori = self.cross_area


def calc_area(
    volume_list: Union[List[int], List[float]], coefficient: float
) -> List[float]:
    """calculatte the planimetric area based on volume

    Parameters
    ----------
    volume_list : Union[List[int], List[float]]
        volumes
    coefficient : float
        area coefficient

    Returns
    -------
    List[float]
        List of volume
    """
    return [round(volume ** 0.666666666666666 * coefficient) for volume in volume_list]


def calc_confidence_limit(
    is_cross_section: bool,
    user_volume: Union[int, float],
    confidence_limit: float,
) -> Tuple[float, float]:
    """Calculate area based on defined confidence limit

    Parameters
    ----------
    is_cross_section : bool
        cross or long section
    user_volume : Union[int, float]
        user volume
    confidence_limit : float
        confidence limit

    Returns
    -------
    Tuple[float, float]
        volumes
    """

    an_intercept = 2.301
    dec_intercept = 200.0
    fills = py_xxplanb
    if is_cross_section:
        an_intercept = -1.301
        dec_intercept = 0.05
        fills = py_xxsecta

    residual_sum = 0.0
    total_log_volume = 0.0

    for (_, volume, area) in fills:
        log_vol = log10(volume)
        total_log_volume += log_vol

        log_area_y = log10(area)
        log_area_pred = (log_vol * 0.666666666667) + an_intercept
        diff = (log_area_y - log_area_pred) * (log_area_y - log_area_pred)
        residual_sum += diff

    se_model = sqrt(residual_sum / (len(fills) - 1))
    mean_log_volume = total_log_volume / len(fills)

    mean_diff_total = 0.0
    one_over_n = 1.0 / len(fills)

    for (_, volume, area) in fills:
        log_vol = log10(volume)
        diff_log_mean = log_vol - mean_log_volume
        diff_squared = diff_log_mean ** 2

        mean_diff_total += diff_squared

    crossttabll = py_xxttabl[len(fills) - 2]
    cross_section_data = crossttabll[confidence2index[str(confidence_limit)]]

    area_up: float = 0.0
    area_dn: float = 0.0
    if cross_section_data is not None:
        log_user_volume = log10(user_volume)
        user_regress_area = round((user_volume ** 0.66666666666667) * dec_intercept)

        diff_mean = log_user_volume - mean_log_volume
        diff_mean_sq = diff_mean ** 2

        sem = se_model * sqrt(one_over_n + (diff_mean_sq / mean_diff_total))
        sep = sqrt((se_model ** 2) + (sem ** 2))

        area_up = 10 ** ((cross_section_data * sep) + log10(user_regress_area))
        area_dn = 10 ** (log10(user_regress_area) - (cross_section_data * sep))

    return area_up, area_dn


def calc_cell_dimension(dem: rasterio.DatasetReader) -> Tuple[float, float]:
    """calculate cell diagonal and width

    Parameters
    ----------
    dem : rasterio.DatasetReader
        DEM file read by rasterio

    Returns
    -------
    Tuple[float, float]
        width and diagonal
    """
    width = dem.transform[0]
    diagonal = round(sqrt((width ** 2) * 2) * 100) / 100
    return width, diagonal


def append_point2array(
    row: int, col: int, planimetrics: PlanimetricData
) -> PlanimetricData:
    """

    Parameters
    ----------
    row : int
        [description]
    col : int
        [description]
    planimetrics : PlanimetricData
        [description]

    Returns
    -------
    PlanimetricData
        [description]
    """
    cross_area_count = len(planimetrics.cross_area) + 1
    dem_value = planimetrics.array[row, col]

    if dem_value == 1:
        planimetrics.array[row, col] = cross_area_count
        planimetrics.value[cross_area_count - 2] += 1
    elif dem_value < cross_area_count:
        planimetrics.array[row, col] = cross_area_count
        planimetrics.value[dem_value - 2] -= 1
        planimetrics.value[cross_area_count - 2] += 1

    return planimetrics


def get_next_cell(
    row: int,
    col: int,
    cell_side: int,
    flow_direction: int,
    dem_array: np.ndarray,
    no_data: float = 99999.0,
) -> Tuple[int, int, Union[int, float]]:
    """get next cell whether left or downward

    Parameters
    ----------
    row : int
    col : int
    cell_side : int
    flow_direction : int
    dem_array : np.ndarray
    no_data : float, optional
        no data, by default 99999.0

    Returns
    -------
    Tuple[int, int, Union[int, float]]
        row, col, elevation

    Raises
    ------
    ValueError
        Flow doesn't follow d8 flow style
    """
    if flow_direction in [1, 2, 4, 8, 16, 32, 64, 128]:
        row_operator, col_operator = next_cell[flow_direction]
    else:
        raise ValueError(f"Bad flow direction {flow_direction}")

    original_x, original_y = row, col
    row += cell_side * row_operator
    col += cell_side * col_operator

    try:
        elevation = dem_array[row, col]
    except IndexError:
        row, col = original_x, original_y
        elevation = no_data

    return row, col, elevation


def create_cross_area(
    first_elevation: float,
    second_elevation: float,
    cell_dimension: float,
    cross_areas: List[float],
    cell_count: int = 1,
) -> List[float]:
    """calculate the cross area of lahar inundation

    Parameters
    ----------
    first_elevation : float
        first elevation
    second_elevation : float
        second elevation
    cell_dimension : float
        width
    cross_areas : List[float]
        list of cross areas
    cell_count : int, optional
        [description], by default 1

    Returns
    -------
    List[float]
        [description]
    """
    cross_areas = [
        area - ((first_elevation - second_elevation) * (cell_dimension * cell_count))
        for area in cross_areas
    ]
    if len(cross_areas) > 1:
        # Remove negative value
        cross_areas = list(filter(lambda x: x > 0, cross_areas))
    return cross_areas


def calc_cross_section(
    dem: DEMData,
    flow_direction: int,
    row_col: Tuple[int, int],
    planimetrics: PlanimetricData,
) -> PlanimetricData:
    cell_dimension = dem.cell_width
    if flow_direction in [8, 128, 2, 32]:
        cell_dimension = dem.cell_diagonal

    right_x, right_y = row_col

    if flow_direction not in [1, 2, 4, 8, 16, 32, 64, 128]:
        raise ValueError(f"out of bound, direction: {flow_direction}")
    left_x, left_y = left_cell[flow_direction](right_x, right_y)

    try:
        left_elevation = dem.array[left_x, left_y]
        right_elevation = dem.array[right_x, right_y]
    except IndexError:
        return planimetrics

    fill_elevation = right_elevation
    count = 0
    cell_norm = 1
    cell_wneg = -1
    cell_count = 0

    while (
        count < 1000000000
        and planimetrics.cross_area
        and planimetrics.cross_area[0] > 0
    ):
        if left_elevation == fill_elevation:
            planimetrics = append_point2array(left_x, left_y, planimetrics)
            left_x, left_y, left_elevation = get_next_cell(
                left_x, left_y, cell_norm, flow_direction, dem.array
            )
            cell_count += 1
        elif right_elevation == fill_elevation:
            planimetrics = append_point2array(right_x, right_y, planimetrics)
            right_x, right_y, right_elevation = get_next_cell(
                right_x, right_y, cell_wneg, flow_direction, dem.array
            )
            cell_count += 1

        elif right_elevation < fill_elevation:
            planimetrics.cross_area = create_cross_area(
                fill_elevation, right_elevation, cell_dimension, planimetrics.cross_area
            )
            cell_count += 1
            if planimetrics.cross_area and planimetrics.cross_area[0] > 0:
                planimetrics = append_point2array(right_x, right_y, planimetrics)
                right_x, right_y, right_elevation = get_next_cell(
                    right_x, right_y, cell_wneg, flow_direction, dem.array
                )

        elif left_elevation < fill_elevation:
            planimetrics.cross_area = create_cross_area(
                fill_elevation, left_elevation, cell_dimension, planimetrics.cross_area
            )
            cell_count += 1
            if planimetrics.cross_area and planimetrics.cross_area[0] > 0:
                planimetrics = append_point2array(left_x, left_y, planimetrics)
                left_x, left_y, left_elevation = get_next_cell(
                    left_x, left_y, cell_norm, flow_direction, dem.array
                )

        elif right_elevation == left_elevation:
            planimetrics.cross_area = create_cross_area(
                right_elevation,
                fill_elevation,
                cell_dimension,
                planimetrics.cross_area,
                cell_count,
            )

            if planimetrics.cross_area and planimetrics.cross_area[0] > 0:
                fill_elevation = right_elevation
                planimetrics = append_point2array(left_x, left_y, planimetrics)
                left_x, left_y, left_elevation = get_next_cell(
                    left_x, left_y, cell_norm, flow_direction, dem.array
                )

                planimetrics = append_point2array(right_x, right_y, planimetrics)
                right_x, right_y, right_elevation = get_next_cell(
                    right_x, right_y, cell_wneg, flow_direction, dem.array
                )
                cell_count += 2

        elif right_elevation > left_elevation:
            planimetrics.cross_area = create_cross_area(
                left_elevation,
                fill_elevation,
                cell_dimension,
                planimetrics.cross_area,
                cell_count,
            )
            cell_count += 1
            if planimetrics.cross_area and planimetrics.cross_area[0] > 0:
                fill_elevation = left_elevation
                planimetrics = append_point2array(left_x, left_y, planimetrics)
                left_x, left_y, left_elevation = get_next_cell(
                    left_x, left_y, cell_norm, flow_direction, dem.array
                )

        elif right_elevation < left_elevation:
            planimetrics.cross_area = create_cross_area(
                right_elevation,
                fill_elevation,
                cell_dimension,
                planimetrics.cross_area,
                cell_count,
            )
            cell_count += 1
            if planimetrics.cross_area and planimetrics.cross_area[0] > 0:
                fill_elevation = right_elevation
                planimetrics = append_point2array(right_x, right_y, planimetrics)
                right_x, right_y, left_elevation = get_next_cell(
                    right_x, right_y, cell_wneg, flow_direction, dem.array
                )

        if left_elevation == 99999.0 or right_elevation == 99999.0:
            planimetrics.cross_area = [-99999 for _ in planimetrics.cross_area]

        count += 1
    planimetrics.restore()
    return planimetrics


def read_volumes(volume_file: Union[Path, str]) -> List[int]:
    with open(volume_file) as volume_reader:
        volumes = [round(float(line)) for line in volume_reader]
    return volumes


# def read_coordinates(coordinates_file: Union[Path, str]) -> List[List[int]]:
#     with open(coordinates_file) as coordinate_reader:
#         coordinates = []
#         for line in coordinate_reader:
#             if "," in line:
#                 coordinate = [round(float(c)) for c in line.split(",")]
#                 coordinates.append(coordinate)
#     return sorted(coordinates)


def calc_cross_planimetric(
    volumes: List[int], confidence_limit: float
) -> Tuple[List[float], List[float]]:
    cross_section_areas = calc_area(volumes, 0.05)
    planimetric_areas = calc_area(volumes, 200)

    cross_section_area1, cross_section_area3 = calc_confidence_limit(
        True, volumes[0], confidence_limit
    )

    planimetric_area1, planimetric_area3 = calc_confidence_limit(
        False, volumes[0], confidence_limit
    )

    cross_section_areas += [round(cross_section_area1), round(cross_section_area3)]
    planimetric_areas += [round(planimetric_area1), round(planimetric_area3)]

    return sorted(cross_section_areas, reverse=True), sorted(
        planimetric_areas, reverse=True
    )


@dataclass
class StartPoint:
    coordinate: List[int]
    volume: int

    @property
    def x(self) -> int:
        return self.coordinate[0]

    @property
    def y(self) -> int:
        return self.coordinate[1]

    def to_rowcol(
        self, up_right_y: float, low_left_x: float, cell_width: float
    ) -> None:
        row = int((up_right_y - self.y) / cell_width)
        col = int((self.x - low_left_x) / cell_width)
        self.row: int = row
        self.col: int = col


def read_coordinates(file_location: str, input_volume: int = -1) -> List[StartPoint]:
    coordinates: List[StartPoint] = []
    with open(file_location) as file:
        for line in file.readlines():
            if "," in line:
                coordinate = [round(float(c)) for c in line.split(",")]
                if len(coordinate) > 3:
                    raise ValueError("only accept 2D coordinate")

                volume = input_volume
                if input_volume == -1 and len(coordinate) < 3:
                    raise ValueError("Please define volume in GUI or coordinate file")
                if input_volume == -1 and len(coordinate) == 3:
                    volume = coordinate[2]

                coordinates.append(StartPoint(coordinate[:3], volume))

    return coordinates


def create_lahar_inundation(
    start_point: StartPoint,
    dem: DEMData,
    direction_array: np.ndarray,
    confidence_limit: Union[int, float],
) -> Tuple[PlanimetricData, List[float]]:
    cross_section_areas, planimetric_areas = calc_cross_planimetric(
        [start_point.volume], confidence_limit
    )

    check_planimetric_extent = planimetric_areas.copy()
    row = start_point.row
    col = start_point.col

    planimetrics = PlanimetricData(
        value=[0 for _ in range(len(check_planimetric_extent))],
        array=np.ones(direction_array.shape, dtype=int),
        cross_area=cross_section_areas,
    )

    cell_traverse_count = 0
    current_flow_direction = direction_array[row, col]
    all_stop = False

    try:
        while (
            not all_stop
            and cell_traverse_count < 90000000
            and current_flow_direction != 0
        ):
            planimetrics = calc_cross_section(
                dem,
                current_flow_direction,
                (row, col),
                planimetrics,
            )
            first_direction, second_direction = cardinal_first.get(
                current_flow_direction, (None, current_flow_direction)
            )
            original_direction = current_flow_direction
            if first_direction is not None:
                planimetrics = calc_cross_section(
                    dem,
                    first_direction,
                    (row, col),
                    planimetrics,
                )
                planimetrics = calc_cross_section(
                    dem,
                    second_direction,
                    (row, col),
                    planimetrics,
                )
            first_direction, second_direction = cardinal_second.get(
                second_direction, (None, 0)
            )
            if first_direction is not None:
                planimetrics = calc_cross_section(
                    dem,
                    first_direction,
                    (row, col),
                    planimetrics,
                )
                planimetrics = calc_cross_section(
                    dem,
                    second_direction,
                    (row, col),
                    planimetrics,
                )
            current_flow_direction = original_direction
            if current_flow_direction in [2, 8, 32, 128]:
                _row, _col = checker_board[current_flow_direction](row, col)
                planimetrics = calc_cross_section(
                    dem,
                    current_flow_direction,
                    (_row, _col),
                    planimetrics,
                )
            planimetrics.value.reverse()
            sigma_value = 0.0
            temp_plan: List[float] = []
            for value in planimetrics.value:
                sigma_value += value
                temp_plan.append(sigma_value * dem.cell_width * dem.cell_width)
            temp_plan.reverse()
            check_planimetric_extent = [
                planimetric_areas[i] - temp_plan[i]
                for i, _ in enumerate(check_planimetric_extent)
            ]

            planimetrics.value.reverse()

            if len(check_planimetric_extent) > 1:
                for _, p in enumerate(check_planimetric_extent):
                    if p < 0:
                        planimetrics.pop_cross()
                        planimetric_areas.pop()
                        cross_section_areas.pop()
                        check_planimetric_extent.pop()
            if check_planimetric_extent[0] < 0:
                break
            row, col = move_downstream[current_flow_direction](row, col)
            current_flow_direction = direction_array[row, col]
            cell_traverse_count += 1
            check_end = direction_array[row - 5 : row + 5, col - 5 : col + 5] == 255

            if sum(check_end.ravel()) > 5:
                print(
                    f"volume too big: {start_point.volume}, there are leftover: {check_planimetric_extent}"
                )
                raise CrossSectionTooLong
            if current_flow_direction == 255:
                print(f"finished at blank, row:{row}, col:{col}")
                raise CrossSectionTooLong

        return planimetrics, check_planimetric_extent
    except CrossSectionTooLong:
        return planimetrics, check_planimetric_extent


def save_result(
    inundation: np.ndarray,
    volume: int,
    output_folder: Path,
    index: int,
    schema: RasterioMeta,
    format: str,
) -> None:
    if format == "raster":
        with rasterio.open(
            output_folder / f"stream_{index}_{volume}.tif", "w", **schema
        ) as output:
            output.write(inundation, 1)
    elif format == "multi_vector":
        union_features = polygonize(
            inundation,
            schema["transform"],
            inundation != 1,
            lambda x: x["properties"]["raster_val"],
        )
        with fiona.open(
            output_folder / f"stream_{index}_{volume}.shp",
            "w",
            driver="ESRI Shapefile",
            crs=schema["crs"],
            schema={
                "geometry": "Polygon",
                "properties": OrderedDict([("raster_val", "int")]),
            },
        ) as out:
            out.writerecords(union_features)


def _batch_lahar_inundation(
    input_raster: str,
    start_points: List[StartPoint],
    confidence_limit: float,
    output_folder: str = "",
    output_type: str = "multi_vector",
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    raster_path = Path(input_raster)
    basename = raster_path.name

    if raster_path.is_dir():
        prefix_name = basename
        if basename.endswith("fill"):
            prefix_name = basename.rstrip("fill")
        else:
            raise ValueError(
                f"{basename} is not a name for filled dem. Please follow the convention"
            )

        input_dem = raster_path.absolute()
        input_direction = raster_path.parent.joinpath(f"{prefix_name}dir")
    else:
        prefix_name = raster_path.stem
        if prefix_name.endswith("fill"):
            prefix_name = prefix_name.rstrip("fill")
        else:
            raise ValueError(
                f"{basename} is not a name for filled dem. Please follow the convention"
            )

        input_dem = raster_path.parent.joinpath(
            f"{prefix_name}fill{raster_path.suffix}"
        )
        input_direction = raster_path.parent.joinpath(
            f"{prefix_name}dir{raster_path.suffix}"
        )

    with rasterio.open(input_dem) as fill_file, rasterio.open(
        input_direction
    ) as direction_file:

        dem_array = fill_file.read(1)
        direction_array = direction_file.read(1)

        schema = RasterioMeta(
            **{
                "driver": "GTiff",
                "count": 1,
                "crs": direction_file.crs,
                "dtype": np.int32,
                "transform": direction_file.transform,
                "height": direction_array.shape[0],
                "width": direction_array.shape[1],
            }
        )

        cell_width, cell_diagonal = calc_cell_dimension(fill_file)

        low_left_x = fill_file.bounds.left
        up_right_y = fill_file.bounds.top

        dem = DEMData(
            array=dem_array,
            cell_diagonal=cell_diagonal,
            cell_width=cell_width,
        )

    output_stream: Path = Path(output_folder)
    if not output_folder.strip():
        output_stream = raster_path.parent / "stream"
        if not output_stream.exists():
            output_stream.mkdir(exist_ok=False)

    progress_total = len(start_points)
    for i, start_point in tqdm(enumerate(start_points)):
        if start_point.volume > 32:
            start_point.to_rowcol(up_right_y, low_left_x, cell_width)

            planimetrics, check_planimetric_extent = create_lahar_inundation(
                start_point,
                dem,
                direction_array,
                confidence_limit,
            )

            while check_planimetric_extent[0] > 0 or planimetrics.last_count > 5000:
                # print(f"Volume {start_point.volume} is too big. Reduce by 20")
                if check_planimetric_extent[0] > 10000:
                    start_point.volume -= int(check_planimetric_extent[0] / 10000 * 50)
                else:
                    start_point.volume -= 20

                if start_point.volume < 32:
                    start_point.volume = 32
                    break

                planimetrics, check_planimetric_extent = create_lahar_inundation(
                    start_point,
                    dem,
                    direction_array,
                    confidence_limit,
                )

            save_result(
                planimetrics.array,
                start_point.volume,
                output_stream,
                i,
                schema,
                output_type,
            )

            # with rasterio.open(
            #     output_stream / f"stream_{i}_{start_point.volume}.tif", "w", **schema
            # ) as output:
            #     output.write(planimetrics.array, 1)
        else:
            print(f"skipping point {i}. volume is below minimum")

        if progress_callback is not None:
            progress_callback(progress_total, i + 1)

    print(f"Done! {len(start_points)} points")
    print(f"Saved at {output_stream}")


def batch_lahar_inundation(
    input_raster: str,
    input_coordinates: str,
    confidence_limit: float,
    input_volume: Union[None, float, int] = None,
    output_folder: str = "",
    output_type: str = "multi_vector",
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    _input_volume: int = -1
    if input_volume is not None:
        _input_volume = int(input_volume)
    start_points = read_coordinates(input_coordinates, _input_volume)
    _batch_lahar_inundation(
        input_raster,
        start_points,
        confidence_limit,
        output_folder,
        output_type,
        progress_callback,
    )
