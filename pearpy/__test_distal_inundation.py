from dataclasses import dataclass, field
from math import log10, sqrt
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import click
import numpy as np
import rasterio
from tqdm.autonotebook import tqdm

from .textfile._textfile import py_xxplanb, py_xxsecta, py_xxttabl


def txt2list(file_name, data_type, use_confidence_limit):
    with open(file_name) as input_file:
        if use_confidence_limit and data_type == "volumes":
            dataset = [round(float(line)) for line in input_file]
        else:
            dataset = []
            if data_type == "volume":
                dataset = [round(float(c)) for c in input_file.readline().split(",")]
            else:
                for line in input_file:
                    if "," in line:
                        coordinates = [round(float(c)) for c in line.split(",")]
                        dataset.append(coordinates)
                dataset.sort()

    return dataset


def text2list(file_name: str) -> List[List[float]]:
    with open(file_name) as input_file:
        dataset = [
            [round(float(coordinate)) for coordinate in line.split(",")]
            for line in input_file
            if "," in line
        ]

    return sorted(dataset)


confidence2index = {"50": 1, "70": 2, "80": 3, "90": 4, "95": 5, "97.5": 6, "99": 7}

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

checker_board = {
    8: lambda r, c: (r + 1, c),
    32: lambda r, c: (r, c - 1),
    128: lambda r, c: (r - 1, c),
    2: lambda r, c: (r, c + 1),
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

cardinal_first = {32: (16, 64), 128: (64, 1), 2: (1, 4), 8: (4, 16)}
cardinal_second = {1: (128, 2), 4: (2, 8), 16: (8, 32), 64: (32, 128)}


@dataclass
class DEMData:
    array: np.ndarray
    cell_diagonal: float
    cell_width: float


@dataclass
class PlanimetricData:
    value: List[float]
    array: np.ndarray
    cross_area: List[float]
    cross_area_ori: Optional[List[float]] = None
    previous_count: int = 0
    last_count: int = 0

    def __post_init__(self):
        self.cross_area_ori = self.cross_area.copy()

    def restore(self):
        self.cross_area = self.cross_area_ori.copy()

    def pop_cross(self):
        self.cross_area.pop()
        self.cross_area_ori = self.cross_area


def calc_area(volume_list: List[Union[float, int]], coefficient: float) -> List:
    return [round(volume ** 0.666666666666666 * coefficient) for volume in volume_list]


def calc_confidence_limit(
    is_cross_section: bool,
    user_volume: Union[int, float],
    confidence_limit: float,
):
    an_intercept = 2.301
    dec_intercept = 200
    fills = py_xxplanb

    if is_cross_section:
        an_intercept = -1.301
        dec_intercept = 0.05
        fills = py_xxsecta

    residual_sum = 0
    total_log_volume = 0

    for (location, volume, area) in fills:
        log_vol = log10(volume)
        total_log_volume += log_vol

        log_area_y = log10(area)
        log_area_pred = (log_vol * 0.666666666667) + an_intercept
        diff = (log_area_y - log_area_pred) ** 2
        residual_sum += diff

    se_model = sqrt(residual_sum / (len(fills) - 1))
    mean_log_volume = total_log_volume / len(fills)

    mean_diff_total = 0.0
    one_over_n = 1.0 / len(fills)

    for (location, volume, area) in fills:
        log_vol = log10(volume)
        diff_log_mean = log_vol - mean_log_volume
        diff_squared = diff_log_mean ** 2

        mean_diff_total += diff_squared

    crossttabll = py_xxttabl[len(fills) - 2]
    cross_section_data = crossttabll[confidence2index.get(str(confidence_limit))]

    area_up, area_dn = None, None
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
    width = dem.transform[0]
    diagonal = round(width * sqrt(2), 2)
    return width, diagonal


def create_cross_area(
    first_elevation: float,
    second_elevation: float,
    cell_dimension: float,
    cross_areas: List,
    cell_count: int = 1,
) -> List:
    cross_areas = [
        area - ((first_elevation - second_elevation) * (cell_dimension * cell_count))
        for area in cross_areas
    ]
    if len(cross_areas) > 1:
        # Remove negative value
        cross_areas = list(filter(lambda x: x > 0, cross_areas))
        # negatives = 0
        # for cross_area in cross_areas:
        #     if cross_area < 0:
        #         negatives += 1
        # while negatives > 0  and len(cross_areas) > 1:
        #     cross_areas.pop()
        #     negatives -= 1
    return cross_areas


class CrossSectionTooLong(Exception):
    pass


def calc_cross_section(
    dem: DEMData,
    flow_direction: int,
    row_col: Tuple[int, int],
    planimetrics: PlanimetricData,
):
    if flow_direction in [8, 128, 2, 32]:
        cell_dimension = dem.cell_diagonal
    else:
        cell_dimension = dem.cell_width

    right_x, right_y = row_col
    if flow_direction in [1, 2, 4, 8, 16, 32, 64, 128]:
        left_x, left_y = left_cell[flow_direction](right_x, right_y)
    else:
        print("out of bound, no direction")
        return planimetrics
        # raise ValueError(f"Bad flow direction: {flow_direction}")
    left_elevation = dem.array[left_x, left_y]
    right_elevation = dem.array[right_x, right_y]

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
        # print(planimetrics.cross_area)
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
        # print("calc_cross",planimetrics.value,planimetrics.cross_area,count, right_elevation, left_elevation, fill_elevation)
        count += 1
    # print("cross area",planimetrics.cross_area, count)
    planimetrics.last_count = count
    if count > 5000:
        print(f"cross count: {count}")
        raise CrossSectionTooLong
    planimetrics.previous_count = count
    planimetrics.restore()
    return planimetrics


def append_point2array(
    row: int, col: int, planimetrics: PlanimetricData
) -> PlanimetricData:
    dem_value = planimetrics.array[row, col]
    cross_area_count = len(planimetrics.cross_area) + 1

    if dem_value == 1:
        planimetrics.array[row, col] = cross_area_count
        planimetrics.value[cross_area_count - 2] += 1
    elif dem_value < cross_area_count:
        planimetrics.array[row, col] = cross_area_count
        planimetrics.value[dem_value - 2] -= 1
        planimetrics.value[cross_area_count - 2] += 1

    # print(f"append point2array {cross_area_count} {dem_value}")

    return planimetrics


def get_next_cell(
    row: int,
    col: int,
    cell_side: int,
    flow_direction: int,
    dem_array: np.ndarray,
    no_data=99999.0,
) -> Tuple[int, int, Union[int, float]]:
    if flow_direction in [1, 2, 4, 8, 16, 32, 64, 128]:
        row_operator, col_operator = next_cell[flow_direction]
    else:
        raise ValueError(f"Bad flow direction {flow_direction}")

    original_x, original_y = row, col
    row += cell_side * row_operator
    col += cell_side * col_operator

    elevation = no_data
    # if row > 0 and col > 0:
    try:
        elevation = dem_array[row, col]
    except IndexError:
        row, col = original_x, original_y
        elevation = no_data

    return row, col, elevation

input_raster: str = "temp/test_jpy/dem250fill"
drain_name: str = "tes"
volume_file: str = "temp/test_jpy/volume.txt"
coordinates_file: str = "temp/test_jpy/coordinate.txt"
flow_type: Optional[str] = None
confidence_limit: Optional[float] = "95"


if flow_type in ["Lahar", "Debris_Flow", "Rock_Avalanche"]:
    use_confidence_limit = False
else:
    conf_limit_choice = flow_type
    use_confidence_limit = True
    flow_type = "Lahar"
print(f"{flow_type} selected")
input_raster = Path(input_raster)
basename = input_raster.name


if basename.endswith("fill"):
    prefix_name = basename.rstrip("fill")
fill_name = input_raster.parent.joinpath(f"{prefix_name}fill")
dir_name = input_raster.parent.joinpath(f"{prefix_name}dir")
volume_list = txt2list(volume_file, "volumes", use_confidence_limit)

if use_confidence_limit and not volume_list:
    volume_list.append(volume_list[0])

start_points = txt2list(coordinates_file, "points", use_confidence_limit)
cross_section_areas = []
planimetric_areas = []
if flow_type == "Lahar":
    cross_section_areas = calc_area(volume_list, 0.05)
    planimetric_areas = calc_area(volume_list, 200)
elif flow_type == "Debris_Flow":
    cross_section_areas = calc_area(volume_list, 0.1)
    planimetric_areas = calc_area(volume_list, 20)
elif flow_type == "Rock_Avalanche":
    cross_section_areas = calc_area(volume_list, 0.2)
    planimetric_areas = calc_area(volume_list, 20)
if use_confidence_limit:
    one_volume = volume_list[0]
    cross_section_area1, cross_section_area3 = calc_confidence_limit(
        True, one_volume, confidence_limit
    )
    planimetric_area1, planimetric_area3 = calc_confidence_limit(
        False, one_volume, confidence_limit
    )
    cross_section_areas += [round(cross_section_area1), round(cross_section_area3)]
    planimetric_areas += [round(planimetric_area1), round(planimetric_area3)]

def calc_cross_planimetric(volumes: List[List[int]], confidence_limit:float):
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

    return sorted(cross_section_areas,reverse=True), sorted(pl
    
volume_list.sort(reverse=True)
cross_section_areas.sort(reverse=True)
planimetric_areas.sort(reverse=True)
check_planimetric_extent = planimetric_areas.copy()

with rasterio.open(fill_name) as fill_file, rasterio.open(
    dir_name
) as direction_file:
    schema = {
        "driver": "GTiff",
        "count": 1,
        "crs": direction_file.crs,
        "transform": direction_file.transform,
    }
    fill_array = fill_file.read(1)
    direction_array = direction_file.read(1)
    cell_width, cell_diagonal = calc_cell_dimension(fill_file)
    w_x_min = 0
    w_x_max = fill_array.shape[0] - 1
    w_y_min = 0
    w_y_max = fill_array.shape[1] - 1
    low_left_x = fill_file.bounds.left
    low_left_y = fill_file.bounds.bottom
    up_right_x = fill_file.bounds.right
    up_right_y = fill_file.bounds.top

for point_index, (curr_x, curr_y) in tqdm(enumerate(start_points)):
    row = int((up_right_y - curr_y) / cell_width)
    col = int((curr_x - low_left_x) / cell_width)
    dem = DEMData(
        array=fill_array, cell_diagonal=cell_diagonal, cell_width=cell_width
    )
    planimetrics = PlanimetricData(
        value=[0 for _ in range(len(check_planimetric_extent))],
        array=np.ones(direction_array.shape, np.int32),
        cross_area=cross_section_areas,
    )
    cell_traverse_count = 0
    all_stop = False
    curr_flow_direction = direction_array[row, col]
    try:
        while not all_stop and cell_traverse_count < 90000000:
            planimetrics = calc_cross_section(
                dem, curr_flow_direction, (row, col), planimetrics,
            )
            first_direction, second_direction = cardinal_first.get(curr_flow_direction, (None,curr_flow_direction))
            original_direction = curr_flow_direction
            # print(f"flowdir: {curr_flow_direction} {first_direction}")
            if first_direction is not None:
                # print(f"first cardinal {first_direction} {second_direction}")
                planimetrics = calc_cross_section(
                    dem, first_direction, (row, col), planimetrics,
                )

                planimetrics = calc_cross_section(
                    dem, second_direction, (row, col), planimetrics,
                )


            first_direction, second_direction = cardinal_second.get(second_direction, (None, None))
            if first_direction is not None:
                # print(f"second cardinal {first_direction} {second_direction}")
                planimetrics = calc_cross_section(
                    dem, first_direction, (row, col), planimetrics,
                )
                planimetrics = calc_cross_section(
                        dem, second_direction, (row, col), planimetrics,
                    )
            curr_flow_direction = original_direction

            if curr_flow_direction in [2, 8, 32, 128]:
                _row, _col = checker_board[curr_flow_direction](row, col)
                planimetrics = calc_cross_section(
                    dem, curr_flow_direction, (_row, _col), planimetrics,
                )

            planimetrics.value.reverse()

            sigma_value = 0
            temp_plan = []
            for i, value in enumerate(planimetrics.value):
                sigma_value += value
                temp_plan.append(sigma_value * cell_width * cell_width)
            temp_plan.reverse()

            check_planimetric_extent = [
                planimetric_areas[i] - temp_plan[i]
                for i, _ in enumerate(check_planimetric_extent)
            ]
            planimetrics.value.reverse()

            planimetrics_length = len(check_planimetric_extent)
            if len(check_planimetric_extent) > 1:
                for _, p in enumerate(check_planimetric_extent):
                    if p < 0:
                        planimetrics.pop_cross()
                        planimetric_areas.pop()
                        cross_section_areas.pop()
                        check_planimetric_extent.pop()

            if check_planimetric_extent[0] < 0:
                break
            row, col = move_downstream[curr_flow_direction](row, col)
            curr_flow_direction = direction_array[row, col]
            cell_traverse_count += 1

            check_end = (direction_array[row-5:row+5,col-5:col+5] == 255).ravel()
            if sum(check_end) > 5:
                print(f"volume too big: {one_volume}, there are leftover: {check_planimetric_extent}")
                break

            if curr_flow_direction == 255:
                print(f"finished at blank, row:{row}, col:{col}")
                break
    except CrossSectionTooLong:
        print(f"Volume too big : {one_volume}, Cross section too long")
