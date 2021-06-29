import os

from PySide2.QtCore import QObject, Slot
from PySide2.QtWidgets import QFileDialog

from ..model.main import MainModel


class MainController(QObject):
    def __init__(self, model: MainModel):
        super().__init__()

        self._model = model

    def open_input_shp(self) -> None:
        file_name = QFileDialog.getOpenFileName(
            self, "select input stream", os.path.expanduser("~")
        )
        if file_name:
            if os.path.exists(str(file_name)):
                self._model.stream_file = str(file_name)
