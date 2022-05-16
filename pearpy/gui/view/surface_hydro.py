import os
from pathlib import Path

from pearpy.gui.model.surface_hydro import SurfaceHydroModel
from pearpy.gui.thread._thread import SignalDict
from pearpy.gui.thread.surface_hydro import SurfaceHydroThread
from pearpy.gui.view.main import BaseOtherView, MainView
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QDialog, QFileDialog


class SurfaceHydroView(BaseOtherView):
    def __init__(self, model: SurfaceHydroModel, root_view: MainView) -> None:
        super().__init__(root_view)
        self.model = model
        self.root.ui.surfacehydro_button_later_dsm.clicked.connect(self.open_later_dsm)
        self.root.ui.surfacehydro_input_later_dsm.textChanged.connect(
            self.on_later_dsm_changed
        )

        self.root.ui.surfacehydro_button_output_folder.clicked.connect(
            self.open_output_location
        )
        self.root.ui.surfacehydro_input_output_folder.textChanged.connect(
            self.on_output_location_changed
        )

        self.root.ui.surfacehydro_input_stream_threshold.textChanged.connect(
            self.on_stream_threshold_change
        )

        self.root.ui.surfacehydro_button_run.clicked.connect(self.run_thread)

    @Slot(str)
    def on_later_dsm_changed(self, value: str) -> None:
        self.model.input_dem = Path(value)

    @Slot(str)
    def on_output_location_changed(self, value: str) -> None:
        self.model.output_directory = Path(value)

    @Slot(str)
    def on_stream_threshold_change(self, value: str) -> None:
        try:
            if value:
                value_float = float(value)
                if not value_float.is_integer():
                    raise ValueError(f"{value_float} is not integer")
                self.model.stream_value = int(value_float)
        except ValueError as err:
            self.root.ui.surfacehydro_input_stream_threshold.setText("0")
            self.root.show_error(str(err))

    def open_later_dsm(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self.root,
            "select later dsm file",
            os.path.expanduser("~"),
            self.supported_raster,
        )
        if file_name is not None and os.path.exists(str(file_name)):
            self.model.input_dem = Path(str(file_name))
            self.root.ui.surfacehydro_input_later_dsm.setText(str(file_name))

    def open_output_location(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self.root, "select output directory"
        )
        if directory:
            self.model.output_directory = Path(str(directory))
            self.root.ui.surfacehydro_input_output_folder.setText(str(directory))

    @Slot(object)
    def on_thread_running(self, value: SignalDict) -> None:
        self.root.ui.startingpoint_progressbar_starting_point.setMaximum(
            value["progress_total"]
        )
        self.root.ui.startingpoint_progressbar_starting_point.setValue(
            self.root.ui.startingpoint_progressbar_starting_point.value() + 1
        )

    @Slot()
    def on_thread_finished(self) -> None:
        self.root.ui.surfacehydro_progressbar.setValue(100)
        self.root.ui.surfacehydro_progressbar.setMaximum(100)
        self.root.root_app.aboutToQuit.disconnect()
        self.root.enable_ui()
        self.root.show_finished()

    @Slot(str)
    def on_error_signal(self, value: str) -> None:
        self.root.ui.surfacehydro_progressbar.setMaximum(100)
        self.root.show_error(value)
        self.root.root_app.aboutToQuit.disconnect()

    def run_thread(self) -> None:
        self._thread = SurfaceHydroThread(self.model, self.root)
        self.root.ui.surfacehydro_progressbar.setMaximum(0)
        self._thread.signals.progress.connect(self.on_thread_running)
        self._thread.signals.finished.connect(self.on_thread_finished)
        self._thread.signals.error.connect(self.on_error_signal)
        self.root.root_app.aboutToQuit.connect(self._thread.stop)
        self._thread.start()
        self.root.disable_ui()
