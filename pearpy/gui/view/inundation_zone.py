import os

from pearpy.gui.model.inundation_zone import InundationModel
from pearpy.gui.thread._thread import SignalDict
from pearpy.gui.thread.inundation import InundationThread
from pearpy.gui.view.main import BaseOtherView, MainView
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QDialog, QFileDialog


class InundationView(BaseOtherView):
    def __init__(self, model: InundationModel, root_view: MainView) -> None:
        super().__init__(root_view)
        self.model = model

        for confidence_limit in self.model.confidence_limit_list:
            self.root.ui.inundation_input_confidence_limit.addItem(
                str(confidence_limit)
            )
        self.root.ui.inundation_input_confidence_limit.setCurrentIndex(5)

        self.root.ui.inundation_button_stream_raster.clicked.connect(
            self.open_input_stream
        )
        self.root.ui.inundation_input_stream_raster.textChanged.connect(
            self.on_stream_raster_changed
        )

        self.root.ui.inundation_button_coordinate_file.clicked.connect(
            self.open_coordinate_file
        )
        self.root.ui.inundation_input_coordinate_file.textChanged.connect(
            self.on_coordinate_file_changed
        )

        self.root.ui.inundation_button_output_folder.clicked.connect(
            self.open_output_folder
        )
        self.root.ui.inundation_input_output_folder.textChanged.connect(
            self.on_output_folder_changed
        )

        self.root.ui.inundation_input_confidence_limit.currentIndexChanged.connect(
            self.on_confidence_limit_changed
        )

        self.root.ui.inundation_button_generate_inundation_zone.clicked.connect(
            self.run_thread
        )

    @Slot(str)
    def on_stream_raster_changed(self, value: str) -> None:
        self.model.stream_raster_file = value

    @Slot(str)
    def on_coordinate_file_changed(self, value: str) -> None:
        self.model.coordinate_file = value

    @Slot(int)
    def on_confidence_limit_changed(self, value: int) -> None:
        self.model.confidence_limit = self.model.confidence_limit_list[value]

    @Slot(str)
    def on_input_volume_changed(self, value: str) -> None:
        if not value:
            self.model.single_volume = None
        else:
            self.model.single_volume = float(value)

    @Slot(str)
    def on_output_folder_changed(self, value: str) -> None:
        self.model.output_folder = value

    @Slot(object)
    def on_thread_running(self, value: SignalDict) -> None:
        self.root.ui.inundation_progressbar_inundation_zone.setMaximum(
            value["progress_total"]
        )
        self.root.ui.inundation_progressbar_inundation_zone.setValue(
            self.root.ui.inundation_progressbar_inundation_zone.value() + 1
        )

    @Slot()
    def on_thread_finished(self) -> None:
        self.root.ui.inundation_progressbar_inundation_zone.setValue(
            self.root.ui.inundation_progressbar_inundation_zone.maximum()
        )
        self.root.root_app.aboutToQuit.disconnect()
        self.root.enable_ui()
        self.root.show_finished()

    @Slot(str)
    def on_error_signal(self, value: str) -> None:
        self.root.ui.inundation_progressbar_inundation_zone.setMaximum(100)
        self.root.show_error(value)
        self.root.root_app.aboutToQuit.disconnect()

    def open_input_stream(self) -> None:
        dialog = QFileDialog(self.root, "Laharz file", os.path.expanduser("~"))
        # dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if dialog.exec_() == QDialog.Accepted:
            self.model.stream_raster_file = dialog.selectedFiles()[0]
            self.root.ui.inundation_input_stream_raster.setText(
                self.model.stream_raster_file
            )

    def open_coordinate_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self.root,
            "select input laharz file",
            os.path.expanduser("~"),
        )
        if file_name is not None and os.path.exists(str(file_name)):
            self.model.coordinate_file = str(file_name)
            self.root.ui.inundation_input_coordinate_file.setText(str(file_name))

    def open_output_folder(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self.root, "select output directory"
        )
        if directory:
            self.model.output_folder = str(directory)
            self.root.ui.inundation_input_output_folder.setText(str(directory))

    def run_thread(self) -> None:
        self._thread = InundationThread(self.model, self.root)
        self.root.ui.inundation_progressbar_inundation_zone.setMaximum(0)
        self._thread.signals.progress.connect(self.on_thread_running)
        self._thread.signals.finished.connect(self.on_thread_finished)
        self._thread.signals.error.connect(self.on_error_signal)
        self.root.root_app.aboutToQuit.connect(self._thread.stop)
        self._thread.start()
        self.root.disable_ui()
