import traceback
from datetime import datetime

from pearpy.distal_inundation import batch_lahar_inundation
from pearpy.gui.model.inundation_zone import InundationModel
from pearpy.gui.thread._thread import CustomThread, SignalDict, ThreadSignals
from PySide2.QtWidgets import QMainWindow


class InundationThread(CustomThread):
    def __init__(self, model: InundationModel, parent: QMainWindow) -> None:
        super().__init__(parent)
        self.signals = ThreadSignals()
        self.model = model

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
        if not self.running:
            raise KeyboardInterrupt("stop by user request")

    def _run(self) -> None:
        batch_lahar_inundation(
            self.model.stream_raster_file,
            self.model.coordinate_file,
            self.model.confidence_limit,
            self.model.single_volume,
            self.model.output_folder,
            self.model.output_type,
            self._progress_callback,
        )

    def _do_work(self) -> None:
        try:
            self._run()
            self.signals.finished.emit()
        except Exception as error:
            traceback.print_exc()
            self.signals.error.emit(str(error))
        if self.running:
            self.stop()
