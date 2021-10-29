import time
from pathlib import Path
from typing import Callable, Optional, Tuple, Union

import whitebox
from geosardine import Raster

wbt = whitebox.WhiteboxTools()


def _create_surface_hydro(
    input_dem: Path,
    out_filled: Path,
    out_direction: Path,
    out_accumulation: Path,
    out_stream_raster: Path,
    stream_value: int,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    """Create surface hidrology data which is needed to generate inundation area.

    Parameters
    ----------
    input_dem : Path
        dem file location
    out_filled : Path
        output location for filled dem (dem without sink)
    out_direction : Path
        output location for flow direction
    out_accumulation : Path
        ouput location for flow accumulation
    out_stream_raster : Path
        ouput location for stream flow
    stream_value : int
        stream threshold to extract stream
    progress_callback : Optional[Callable[[int, int], None]], optional
        to send progress, by default None

    Returns
    -------
    None
    """
    if progress_callback is not None:
        progress_callback(0, 0)

    wbt.fill_depressions(input_dem, out_filled)
    wbt.d8_pointer(out_filled, out_direction, esri_pntr=True)
    wbt.d8_flow_accumulation(out_direction, out_accumulation, pntr=True, esri_pntr=True)
    wbt.extract_streams(
        out_accumulation, out_stream_raster, stream_value, zero_background=True
    )


def generate_output_filenames(
    output_path: Path, input_dem: Path, stream_value: int
) -> Tuple[Path, Path, Path, Path]:
    """generate output filename for each surface hidrology which is needed to generate inundation area.

    Parameters
    ----------
    output_path : Path
        output folder 
    input_dem : Path
        dem file location
    stream_value : int
        stream threshold

    Returns
    -------
    Tuple[Path, Path, Path, Path]
        output location of filled dem, flow direction, flow accumulation, streams
    """
    return (
        output_path.joinpath(f"{input_dem.stem}fill.tif").absolute(),
        output_path.joinpath(f"{input_dem.stem}dir.tif").absolute(),
        output_path.joinpath(f"{input_dem.stem}flac.tif").absolute(),
        output_path.joinpath(f"{input_dem.stem}str{stream_value}.tif").absolute(),
    )


def create_surface_hydro(
    input_dem: Union[str, Path],
    output_directory: Union[str, Path],
    stream_value: int,
    progress_callback: Optional[Callable[[int, int], None]] = None,
):
    """Wrapper to create surface hydrology file

    Parameters
    ----------
    input_dem : Union[str, Path]
        dem file location
    output_directory : Union[str, Path]
        output folder
    stream_value : int
        stream threshold to extract stream
    progress_callback : Optional[Callable[[int, int], None]], optional
        to send progress, by default None
    """
    output_path = Path(output_directory)
    input_dem = Path(input_dem)

    _create_surface_hydro(
        input_dem,
        *generate_output_filenames(output_path, input_dem, stream_value),
        stream_value,
        progress_callback,
    )
