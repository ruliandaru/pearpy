from pathlib import Path

import click

from .distal_inundation import batch_lahar_inundation
from .starting_point import find_starting_points, save2txt


@click.group()
def main() -> None:
    """CLARET Command Line Interface"""
    pass


@main.command("starting-point")
@click.argument("stream")
@click.argument("earlier_dsm")
@click.argument("later_dsm")
@click.option("--output-format", default="txt-laharz", help="output data format")
def starting_points(
    stream: str, earlier_dsm: str, later_dsm: str, out_format: str
) -> None:
    """
    Generate initial points for Laharz by using STREAM , DSM, DSM-DIFF raster
    """
    starting_points = find_starting_points(stream, earlier_dsm, later_dsm)
    stream_path: Path = Path(stream)
    if out_format == "txt-laharz":
        save2txt(
            starting_points, stream_path.parent.joinpath(f"{stream_path.stem}.txt")
        )


@main.command("inundation")
@click.argument("input_raster", type=str)
@click.argument("coordinate_file", type=str)
@click.argument("confidence_limit", type=float)
@click.option(
    "--volume",
    type=str,
    default="-1",
    help="volume input if volume not included in corrdinate file",
)
@click.option(
    "--output_folder",
    type="str",
    default="",
    help="output location, default: same parent folder of input raster",
)
def lahar_inundation(
    input_raster: str,
    input_coordinates: str,
    confidence_limit: float,
    input_volume: str = "-1",
    output_folder: str = "",
) -> None:
    """
    Create lahar inundation zone per each point in COORDINATE_FILE
    based on INPUT_RASTER by using CONFIDENCE_LIMIT
    """
    batch_lahar_inundation(
        input_raster, input_coordinates, confidence_limit, input_volume, output_folder
    )


if __name__ == "__main__":
    main()
