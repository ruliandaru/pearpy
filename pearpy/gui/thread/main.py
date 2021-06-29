import traceback
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional, Tuple

from pearpy.create_surface_hydro import _create_surface_hydro, generate_output_filenames
from pearpy.distal_inundation import StartPoint, _batch_lahar_inundation
from pearpy.gui.model.main import MainModel
from pearpy.gui.thread._thread import CustomThread, SignalDict, ThreadSignals
from pearpy.starting_point2 import find_starting_points, save2txt
from PySide2.QtWidgets import QMainWindow
from shapely.geometry.point import Point


class MainPageThread(CustomThread):
    def __init__(self, model: MainModel, parent: QMainWindow) -> None:
        super().__init__(parent)
        self.signals = ThreadSignals()
        self.model = model

    def _progress_callback_surface_hydro(self, total: int, current: int) -> None:
        self.signals.progress.emit(
            SignalDict(
                progress_total=total,
                progress_current=current,
                progress_type="main",
                timestamp=int(datetime.now().timestamp()),
                description="Generating surface hydro...",
            )
        )
        if not self.running:
            raise KeyboardInterrupt("stop by user request")

    def _progress_callback_startingp(self, total: int, current: int) -> None:
        self.signals.progress.emit(
            SignalDict(
                progress_total=total,
                progress_current=current,
                progress_type="main",
                timestamp=int(datetime.now().timestamp()),
                description="Finding starting points...",
            )
        )
        if not self.running:
            raise KeyboardInterrupt("stop by user request")

    def _progress_callback_inundation(self, total: int, current: int) -> None:
        self.signals.progress.emit(
            SignalDict(
                progress_total=total,
                progress_current=current,
                progress_type="main",
                timestamp=int(datetime.now().timestamp()),
                description="Generating inundation...",
            )
        )
        if not self.running:
            raise KeyboardInterrupt("stop by user request")

    def __run_surface_hydro(self) -> None:
        if isinstance(self.model.temporary_directory, TemporaryDirectory):
            if Path(self.model.temporary_directory.name).exists:
                self.model.temporary_directory.cleanup()

        if self.model.preserve_data:
            output_directory = self.model.output_folder.joinpath("processing_data")
            output_directory.mkdir(exist_ok=True)
        else:
            output_temp_directory = TemporaryDirectory()
            output_directory = Path(output_temp_directory.name)
            self.model.temporary_directory = output_temp_directory

        (filled, direction, accumulation, stream_r) = generate_output_filenames(
            Path(output_directory).absolute(),
            self.model.surface_hydro.input_dem,
            self.model.surface_hydro.stream_value,
        )
        self.model.surface_hydro.dem_filled = filled
        self.model.surface_hydro.flow_direction = direction
        self.model.surface_hydro.flow_accumulation = accumulation
        self.model.surface_hydro.stream_raster = stream_r

        _create_surface_hydro(
            *self.model.surface_hydro.args, self._progress_callback_surface_hydro
        )

    def __run_starting_point(
        self,
    ) -> None:
        _starting_points, _processing_data = find_starting_points(
            self.model.starting_point.earlier_dsm,
            self.model.starting_point.later_dsm,
            str(self.model.surface_hydro.flow_direction),
            str(self.model.surface_hydro.stream_raster),
            self.model.starting_point.max_percent_length,
            self.model.starting_point.stream_buffer_size,
            self.model.preserve_data,
            self._progress_callback_startingp,
        )

        save2txt(
            _starting_points,
            Path(self.model.output_folder).joinpath(
                f"{datetime.now().strftime('%Y%m%d-%H%M')}_starting_point.txt"
            ),
        )

        self.model.starting_point.starting_points = _starting_points
        self.model.starting_point.processing_data = _processing_data

    def __run_inundation(self, starting_points: List[Tuple[Point, float]]) -> None:
        _starting_points = [
            StartPoint([int(sp.x), int(sp.y)], int(v)) for sp, v in starting_points
        ]
        _batch_lahar_inundation(
            str(self.model.surface_hydro.dem_filled),
            _starting_points,
            self.model.inundation.confidence_limit,
            str(self.model.output_folder),
            self.model.inundation.output_type,
            self._progress_callback_inundation,
        )

    def _do_work(self) -> None:
        try:
            self.__run_surface_hydro()
            self.signals.finished.emit()

            self.__run_starting_point()
            self.signals.finished.emit()

            self.__run_inundation(self.model.starting_point.starting_points)
            if self.model.starting_point.processing_data is not None:
                if self.model.preserve_data:
                    self.model.starting_point.processing_data.save(
                        self.model.output_folder.joinpath("processing_data")
                    )
                self.model.starting_point.reset()

            if self.model.temporary_directory is not None:
                if Path(self.model.temporary_directory.name).exists():
                    self.model.temporary_directory.cleanup()

            self.signals.finished.emit()
        except Exception as error:
            traceback.print_exc()
            self.model.starting_point.reset()

            if self.model.temporary_directory is not None:
                if Path(self.model.temporary_directory.name).exists():
                    self.model.temporary_directory.cleanup()
            self.signals.error.emit(str(error))
        if self.running:
            self.stop()
