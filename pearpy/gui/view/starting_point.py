import os

from pearpy.gui.model.starting_point import StartingPointModel
from pearpy.gui.thread._thread import SignalDict
from pearpy.gui.thread.starting_point import StartingPointThread
from pearpy.gui.view.main import BaseOtherView, MainView
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QDialog, QFileDialog


class StartingPointView(BaseOtherView):
    def __init__(self, model: StartingPointModel, root_view: MainView) -> None:
        super().__init__(root_view)
        self.model = model

        self.root.ui.startingpoint_button_flow_directoin.clicked.connect(
            self.open_flow_direction
        )
        self.root.ui.startingpoint_input_flow_directoin.textChanged.connect(
            self.on_flow_direction_changed
        )

        self.root.ui.startingpoint_button_stream.clicked.connect(self.open_stream_file)
        self.root.ui.startingpoint_input_stream.textChanged.connect(
            self.on_stream_changed
        )

        self.root.ui.startingpoint_button_earlier_dsm.clicked.connect(
            self.open_earlier_dsm
        )
        self.root.ui.startingpoint_input_earlier_dsm.textChanged.connect(
            self.on_earlier_dsm_changed
        )

        self.root.ui.startingpoint_button_later_dsm.clicked.connect(self.open_later_dsm)
        self.root.ui.startingpoint_input_later_dsm.textChanged.connect(
            self.on_later_dsm_changed
        )

        self.root.ui.startingpoint_button_output_location.clicked.connect(
            self.open_output_location
        )
        self.root.ui.startingpoint_input_output_location.textChanged.connect(
            self.on_output_folder_changed
        )

        self.root.ui.startingpoint_button_find_starting_point.clicked.connect(
            self.run_thread
        )

        self.root.ui.startingpoint_input_stream_buffer.setText(
            str(self.model.stream_buffer_size)
        )
        self.root.ui.startingpoint_input_max_pct_stream.setText(
            str(self.model.max_percent_length)
        )

        self.root.ui.startingpoint_input_stream_buffer.textChanged.connect(
            self.on_stream_buffer_changed
        )
        self.root.ui.startingpoint_input_max_pct_stream.textChanged.connect(
            self.on_max_percent_changed
        )

    @Slot(str)
    def on_stream_buffer_changed(self, value: str):
        try:
            if len(value) == 0:
                value = "0"
                self.root.ui.startingpoint_input_stream_buffer.setText(value)

            if float(value) < 0:
                value = "0"
                self.root.ui.startingpoint_input_stream_buffer.setText(value)

            self.model.stream_buffer_size = float(value)
        except ValueError:
            value = "0"
            self.root.ui.startingpoint_input_stream_buffer.setText(value)
            self.model.stream_buffer_size = float(value)

    @Slot(str)
    def on_max_percent_changed(self, value: str) -> None:
        try:
            if len(value) == 0:
                value = "0"
                self.root.ui.startingpoint_input_max_pct_stream.setText(value)

            if float(value) < 0:
                value = "0"
                self.root.ui.startingpoint_input_max_pct_stream.setText(value)
            elif float(value) > 100:
                value = "100"
                self.root.ui.startingpoint_input_max_pct_stream.setText(value)

            self.model.stream_buffer_size = float(value)
        except ValueError:
            value = "0"
            self.root.ui.startingpoint_input_max_pct_stream.setText(value)
            self.model.stream_buffer_size = float(value)

    @Slot(str)
    def on_flow_direction_changed(self, value: str) -> None:
        self.model.flow_direction = value

    @Slot(str)
    def on_stream_changed(self, value: str) -> None:
        self.model.stream = value

    @Slot(str)
    def on_earlier_dsm_changed(self, value: str) -> None:
        self.model.earlier_dsm = value

    @Slot(str)
    def on_later_dsm_changed(self, value: str) -> None:
        self.model.later_dsm = value

    @Slot(str)
    def on_output_folder_changed(self, value: str) -> None:
        self.model.output_folder = value

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
        self.root.ui.startingpoint_progressbar_starting_point.setValue(
            self.root.ui.startingpoint_progressbar_starting_point.maximum()
        )
        self.root.root_app.aboutToQuit.disconnect()
        self.root.enable_ui()
        self.root.show_finished()

    @Slot(str)
    def on_error_signal(self, value: str) -> None:
        self.root.ui.startingpoint_progressbar_starting_point.setMaximum(100)
        self.root.show_error(value)
        self.root.root_app.aboutToQuit.disconnect()
        # self._thread.stop()

    def open_flow_direction(self) -> None:
        dialog = QFileDialog(self.root, "Flow direction", os.path.expanduser("~"))
        dialog.setFileMode(QFileDialog.ExistingFile)
        # dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if dialog.exec_() == QDialog.Accepted:
            self.model.flow_direction = dialog.selectedFiles()[0]
            self.root.ui.startingpoint_input_flow_directoin.setText(
                self.model.flow_direction
            )

    def open_stream_file(self) -> None:
        dialog = QFileDialog(self.root, "Stream file", os.path.expanduser("~"))
        dialog.setFileMode(QFileDialog.ExistingFile)
        # dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if dialog.exec_() == QDialog.Accepted:
            self.model.stream = dialog.selectedFiles()[0]
            self.root.ui.startingpoint_input_stream.setText(self.model.stream)
        # file_name, _ = QFileDialog.getOpenFileName(
        #     self.root,
        #     "select input laharz file",
        #     os.path.expanduser("~"),
        #     self.supported_raster,
        # )
        # if file_name is not None and os.path.exists(str(file_name)):
        #     self.model.laharz_file = str(file_name)
        #     self.root.ui.startingpoint_input_laharz_file.setText(str(file_name))

    def open_earlier_dsm(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self.root,
            "select input earlier dsm raster",
            os.path.expanduser("~"),
            self.supported_raster,
        )
        if file_name is not None and os.path.exists(str(file_name)):
            self.model.earlier_dsm = str(file_name)
            self.root.ui.startingpoint_input_earlier_dsm.setText(str(file_name))

    def open_later_dsm(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self.root,
            "select input later dsm raster",
            os.path.expanduser("~"),
            self.supported_raster,
        )
        if file_name is not None and os.path.exists(str(file_name)):
            self.model.later_dsm = str(file_name)
            self.root.ui.startingpoint_input_later_dsm.setText(str(file_name))

    def open_output_location(self) -> None:
        output_file, _ = QFileDialog.getSaveFileName(
            self.root, "select output directory"
        )
        if len(output_file) > 0:
            self.model.output_file = str(output_file)
            self.root.ui.startingpoint_input_output_location.setText(str(output_file))

    def run_thread(self) -> None:
        self._thread = StartingPointThread(self.model, self.root)
        self.root.ui.startingpoint_progressbar_starting_point.setMaximum(0)
        self._thread.signals.progress.connect(self.on_thread_running)
        self._thread.signals.finished.connect(self.on_thread_finished)
        self._thread.signals.error.connect(self.on_error_signal)
        self.root.root_app.aboutToQuit.connect(self._thread.stop)
        self._thread.start()
        self.root.disable_ui()
