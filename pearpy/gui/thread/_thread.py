import sys
import threading

if sys.version_info >= (3, 8):
    from typing import Any, TypedDict
else:
    try:
        from typing import Any

        from typing_extensions import TypedDict
    except ImportError:
        raise ImportError("Please install typing_extension to be able use TypedDict")

from PySide2.QtCore import QObject, QThread, Signal
from PySide2.QtWidgets import QMainWindow


class SignalDict(TypedDict):
    progress_type: str
    progress_total: int
    progress_current: int
    timestamp: int
    description: str


class ThreadSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(object)


class CustomThread(QThread):
    def __init__(self, parent: QMainWindow) -> None:
        QThread.__init__(self, parent)

        self.window = parent

        self._lock = threading.Lock()
        self.running = False

    def stop(self) -> None:
        self.running = False
        print("received stop signal from window.")
        with self._lock:
            self._do_before_done()
        self.quit()

    def _do_work(self) -> None:
        print("thread is running...")
        self.sleep(1)

    def _do_before_done(self) -> None:
        print("waiting 2 seconds before thread done..")
        for i in range(2, 0, -1):
            print("{0} seconds left...".format(i))
            self.sleep(1)
        print("ok, thread done.")

    def run(self) -> None:
        self.running = True
        while self.running:
            with self._lock:
                self._do_work()
        self.stop()
