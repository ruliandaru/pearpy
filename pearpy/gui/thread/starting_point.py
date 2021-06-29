import traceback
from datetime import datetime

from pearpy.gui.model.starting_point import StartingPointModel
from pearpy.gui.thread._thread import CustomThread, SignalDict, ThreadSignals
from pearpy.starting_point2 import find_starting_points, save2txt
from PySide2.QtWidgets import QMainWindow


class StartingPointThread(CustomThread):
    def __init__(self, model: StartingPointModel, parent: QMainWindow) -> None:
        super().__init__(parent)
        self.model = model
        self.signals = ThreadSignals()

    def _progress_callback(self, total: int, current: int) -> None:
        self.signals.progress.emit(
            SignalDict(
                progress_total=total,
                progress_current=current,
                progress_type="main",
                timestamp=int(datetime.now().timestamp()),
                description="",
            )
        )

    def _run(self) -> None:
        _starting_points, _ = find_starting_points(
            self.model.earlier_dsm,
            self.model.later_dsm,
            self.model.flow_direction,
            self.model.stream,
            self.model.max_percent_length,
            self.model.stream_buffer_size,
            progress_callback=self._progress_callback,
        )

        save2txt(_starting_points, self.model.output_file)

    def _do_work(self) -> None:
        try:
            self._run()
            self.signals.finished.emit()
        except Exception as error:
            traceback.print_exc()
            self.signals.error.emit(str(error))
        if self.running:
            self.stop()
