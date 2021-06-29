from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

from pearpy.gui.model.inundation_zone import InundationModel
from pearpy.gui.model.starting_point import StartingPointModel
from pearpy.gui.model.surface_hydro import SurfaceHydroModel


@dataclass
class MainModel:
    surface_hydro = SurfaceHydroModel()
    inundation = InundationModel()
    starting_point = StartingPointModel()
    preserve_data: bool = True
    temporary_directory: Optional["TemporaryDirectory"] = None
    output_folder: Path = Path()
