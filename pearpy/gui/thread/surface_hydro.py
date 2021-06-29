import traceback
from datetime import datetime

from pearpy.create_surface_hydro import _create_surface_hydro
from pearpy.distal_inundation import batch_lahar_inundation
from pearpy.gui.model.surface_hydro import SurfaceHydroModel
from pearpy.gui.thread._thread import CustomThread, SignalDict, ThreadSignals
from PySide2.QtWidgets import QMainWindow


class InundationThread(CustomThread):
    def __init__(self, model: SurfaceHydroModel, parent: QMainWindow) -> None:
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
                description="Generating surface hydro...",
            )
        )
        if not self.running:
            raise KeyboardInterrupt("stop by user request")

    def _run(self) -> None:
        _create_surface_hydro(*self.model.args, self._progress_callback)

    def _do_work(self) -> None:
        try:
            self._run()
            self.signals.finished.emit()
        except Exception as error:
            traceback.print_exc()
            self.signals.error.emit(str(error))
        if self.running:
            self.stop()
