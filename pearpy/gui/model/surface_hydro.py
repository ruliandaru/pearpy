from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


@dataclass
class SurfaceHydroModel:
    input_dem: Path = Path()
    dem_filled: Path = Path()
    flow_direction: Path = Path()
    flow_accumulation: Path = Path()
    stream_raster: Path = Path()
    stream_value: int = 250
    output_directory: Path = Path()

    @property
    def args(self) -> Tuple[Path, Path, Path, Path, Path, int]:
        return (
            self.input_dem,
            self.dem_filled,
            self.flow_direction,
            self.flow_accumulation,
            self.stream_raster,
            self.stream_value,
        )
