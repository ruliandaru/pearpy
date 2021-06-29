import sys
from dataclasses import asdict, dataclass

if sys.version_info >= (3, 8):
    from typing import Optional, Tuple, TypedDict
else:
    try:
        from typing import Optional, Tuple

        from typing_extensions import TypedDict
    except ImportError:
        raise ImportError("Please install typing_extension to be able use TypedDict")


class InundationModelDict(TypedDict):
    stream_raster_file: str
    coordinate_file: str
    confidence_limit: float
    single_volume: Optional[float]
    output_folder: str
    output_type: str
    confidence_limit_list: Tuple[float, ...]


@dataclass
class InundationModel:
    stream_raster_file: str = ""
    coordinate_file: str = ""
    confidence_limit: float = 95.0
    single_volume: Optional[float] = None
    output_folder: str = ""
    output_type: str = "multi_vector"
    confidence_limit_list: Tuple[float, ...] = (
        50.0,
        70.0,
        80.0,
        90.0,
        95.0,
        97.5,
        99.0,
    )

    @property
    def dict(self) -> InundationModelDict:
        return InundationModelDict(**asdict(self))
