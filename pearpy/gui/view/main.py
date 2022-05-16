import multiprocessing
import os
from datetime import datetime
from pathlib import Path

from pearpy.gui.model.main import MainModel
from pearpy.gui.thread._thread import SignalDict
from pearpy.gui.thread.main import MainPageThread
from pearpy.gui.view.layout import Ui_MainWindow
from PySide2.QtCore import QObject, QThreadPool, Slot
from PySide2.QtWidgets import (QApplication, QFileDialog, QMainWindow,
                               QMessageBox)


class MainView(QMainWindow):
    def __init__(self, model: MainModel, root_app: QApplication) -> None:
        super().__init__()
        self.root_app = root_app
        self.supported_vector = "ESRI Shapefile (*.shp);;GeoJSON (*.json *.geojson)"
        self.supported_raster = "GeoTIFF (*.tif *.tiff);;All Files (*)"

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.statusbar.showMessage("tkglxm")
        self.thread_pool = QThreadPool()
        self.pool = multiprocessing.Pool(processes=2)

        self.model = model

        for confidence_limit in self.model.inundation.confidence_limit_list:
            self.ui.mainpage_input_confidencelimit.addItem(str(confidence_limit))
        self.ui.mainpage_input_confidencelimit.setCurrentIndex(4)

        self.ui.mainpage_input_confidencelimit.currentIndexChanged.connect(
            self.on_confidence_limit_change
        )

        self.ui.mainpage_button_earlier_dsm.clicked.connect(self.open_earlier_dsm)
        self.ui.mainpage_input_earlier_dsm.textChanged.connect(
            self.on_earlier_dsm_changed
        )

        self.ui.mainpage_button_later_dsm.clicked.connect(self.open_later_dsm)
        self.ui.mainpage_input_later_dsm.textChanged.connect(self.on_later_dsm_changed)

        self.ui.mainpage_button_output_folder.clicked.connect(self.open_output_location)
        self.ui.mainpage_input_output_folder.textChanged.connect(
            self.on_output_location_changed
        )

        self.ui.mainpage_input_streamthreshold.textChanged.connect(
            self.on_stream_threshold_change
        )
        self.ui.mainpage_check_preservedata.stateChanged.connect(
            self.on_preserve_data_change
        )

        self.ui.mainpage_input_stream_buffer.setText(
            str(self.model.starting_point.stream_buffer_size)
        )
        self.ui.mainpage_input_max_pct_stream.setText(
            str(self.model.starting_point.max_percent_length)
        )

        self.ui.mainpage_input_stream_buffer.textChanged.connect(
            self.on_stream_buffer_changed
        )
        self.ui.mainpage_input_max_pct_stream.textChanged.connect(
            self.on_max_percent_changed
        )

        self.ui.mainpage_button_run.clicked.connect(self.run_thread)

        self.ui.output_type.idReleased.connect(self.on_output_type_changed)

    @Slot(str)
    def on_stream_buffer_changed(self, value: str):
        try:
            if len(value) == 0:
                value = "0"
                self.ui.mainpage_input_stream_buffer.setText(value)

            if float(value) < 0:
                value = "0"
                self.ui.mainpage_input_stream_buffer.setText(value)

            self.model.starting_point.stream_buffer_size = float(value)
        except ValueError:
            value = "0"
            self.ui.mainpage_input_stream_buffer.setText(value)
            self.model.starting_point.stream_buffer_size = float(value)

    @Slot(str)
    def on_max_percent_changed(self, value: str) -> None:
        try:
            if len(value) == 0:
                value = "0"
                self.ui.mainpage_input_max_pct_stream.setText(value)

            if float(value) < 0:
                value = "0"
                self.ui.mainpage_input_stream_buffer.setText(value)
            elif float(value) > 100:
                value = "100"
                self.ui.mainpage_input_stream_buffer.setText(value)

            self.model.starting_point.stream_buffer_size = float(value)
        except ValueError:
            value = "0"
            self.ui.mainpage_input_stream_buffer.setText(value)
            self.model.starting_point.stream_buffer_size = float(value)

    @Slot(int)
    def on_output_type_changed(self, value: int) -> None:
        # raster -2 , vector -3
        if value == -2:
            self.model.inundation.output_type = "multi_vector"
        elif value == -3:
            self.model.inundation.output_type = "raster"
        print(value, self.ui.output_type.checkedId())

    @Slot(str)
    def on_earlier_dsm_changed(self, value: str) -> None:
        self.model.starting_point.earlier_dsm = value

    @Slot(str)
    def on_later_dsm_changed(self, value: str) -> None:
        self.model.starting_point.later_dsm = value
        self.model.surface_hydro.input_dem = Path(value)

    @Slot(str)
    def on_output_location_changed(self, value: str) -> None:
        self.model.output_folder = Path(value)

    @Slot(int)
    def on_confidence_limit_change(self, value: int) -> None:
        self.model.inundation.confidence_limit = (
            self.model.inundation.confidence_limit_list[value]
        )

    @Slot(str)
    def on_stream_threshold_change(self, value: str) -> None:
        try:
            if value:
                value_float = float(value)
                if not value_float.is_integer():
                    raise ValueError(f"{value_float} is not integer")
                self.model.surface_hydro.stream_value = int(value_float)
        except ValueError as err:
            self.show_error(str(err))

    @Slot(int)
    def on_preserve_data_change(self, value: int) -> None:
        if value == 0:
            self.model.preserve_data = False
        else:
            self.model.preserve_data = True
        print("on preserve", value, self.model.preserve_data)

    @Slot(str)
    def on_error_signal(self, value: str) -> None:
        self.enable_ui()
        self.show_error(value)
        self.root_app.aboutToQuit.disconnect()

    @Slot(object)
    def on_thread_running(self, value: SignalDict) -> None:
        self.ui.mainpage_label_progressbar_sub.setText(value["description"])
        self.ui.mainpage_progressbar_sub.setMaximum(value["progress_total"])
        self.ui.mainpage_progressbar_sub.setValue(value["progress_current"])

    @Slot(str)
    def on_thread_finished(self) -> None:
        self.ui.mainpage_progressbar_overall.setValue(
            self.ui.mainpage_progressbar_overall.value() + 1
        )

        if self.ui.mainpage_progressbar_overall.value() == 3:
            # self._thread.stop()
            self.root_app.aboutToQuit.disconnect()
            self.enable_ui()
            self.show_finished()

    def open_earlier_dsm(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "select earlier dsm file",
            os.path.expanduser("~"),
            self.supported_raster,
        )
        if file_name is not None and os.path.exists(str(file_name)):
            self.model.starting_point.earlier_dsm = str(file_name)
            self.ui.mainpage_input_earlier_dsm.setText(str(file_name))

    def open_later_dsm(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "select later dsm file",
            os.path.expanduser("~"),
            self.supported_raster,
        )
        if file_name is not None and os.path.exists(str(file_name)):
            self.model.starting_point.later_dsm = str(file_name)
            self.model.surface_hydro.input_dem = Path(str(file_name))
            self.ui.mainpage_input_later_dsm.setText(str(file_name))

    def open_output_location(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "select output directory")
        if directory:
            self.model.output_folder = Path(str(directory))
            self.ui.mainpage_input_output_folder.setText(str(directory))

    def run_thread(self) -> None:
        self._thread = MainPageThread(self.model, self)
        self.ui.mainpage_progressbar_overall.setValue(0)
        self.ui.mainpage_progressbar_overall.setMaximum(3)
        self.ui.mainpage_progressbar_sub.setValue(0)
        self.ui.mainpage_progressbar_sub.setMaximum(0)

        self._thread.signals.progress.connect(self.on_thread_running)
        self._thread.signals.finished.connect(self.on_thread_finished)
        self._thread.signals.error.connect(self.on_error_signal)
        self.root_app.aboutToQuit.connect(self._thread.stop)
        self._thread.start()
        # self.thread_pool.start(self._thread)
        self.disable_ui()

    def show_error(self, error: str) -> None:
        print(error)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setInformativeText(error)
        msg.setWindowTitle("Error")
        msg.exec_()

    def show_finished(self) -> None:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText(f"Finished at {str(datetime.now())} !")
        msg.setWindowTitle("Finished !")
        msg.exec_()

    def disable_ui(self) -> None:
        self.ui.centralwidget.setEnabled(False)

    def enable_ui(self) -> None:
        self.ui.centralwidget.setEnabled(True)


class BaseOtherView(QObject):
    def __init__(self, root_view: MainView) -> None:
        super().__init__()
        self.supported_vector = "ESRI Shapefile (*.shp);;GeoJSON (*.json *.geojson)"
        self.supported_raster = "GeoTIFF (*.tif *.tiff);;All Files (*)"
        self.root = root_view
