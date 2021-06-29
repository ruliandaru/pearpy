import rasterio
from pearpy import __version__, batch_lahar_inundation, find_starting_points
from pearpy.__main__ import starting_points

starting_points()


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_starting_point() -> None:
    points = find_starting_points(
        "tests/data/stream_polyline_no_crater.shp",
        "tests/data/DSM_registrasi ulang T5.tif",
        "tests/data/DSM difference T1-T5_inverted.tif",
    )

    assert len(points) > 0


def test_lahar_inundation() -> None:
    with rasterio.open("tests/data/res384.tif") as source:
        expected = source.read(1)
        batch_lahar_inundation("tests/data/dem250fill", "tests/data/coordinate.txt", 95)

    with rasterio.open("tests/data/stream/stream_0_384.tif") as source:
        assert (expected == source.read(1)).all()
