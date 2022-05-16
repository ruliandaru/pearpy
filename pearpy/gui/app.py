import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pearpy.gui.model.inundation_zone import InundationModel
from pearpy.gui.model.main import MainModel
from pearpy.gui.model.starting_point import StartingPointModel
from pearpy.gui.model.surface_hydro import SurfaceHydroModel
from pearpy.gui.view.inundation_zone import InundationView
from pearpy.gui.view.main import MainView
from pearpy.gui.view.starting_point import StartingPointView
from pearpy.gui.view.surface_hydro import SurfaceHydroView
from PySide2.QtWidgets import QApplication


class App(QApplication):
    def __init__(self, sys_argv: Any) -> None:
        super(App, self).__init__(sys_argv)
        # self.aboutToQuit.connect()
        self.main_view = MainView(MainModel(), self)
        self.starting_point_view = StartingPointView(
            StartingPointModel(), self.main_view
        )
        self.inundation_zone_view = InundationView(InundationModel(), self.main_view)
        self.surface_hydro_view = SurfaceHydroView(SurfaceHydroModel(), self.main_view)
        self.main_view.show()


def main() -> None:
    app = App(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside2"))
    ret = app.exec_()

    if isinstance(app.main_view.model.temporary_directory, TemporaryDirectory):
        if Path(app.main_view.model.temporary_directory.name).exists:
            app.main_view.model.temporary_directory.cleanup()
            print(f"{app.main_view.model.temporary_directory.name} deleted")

    sys.exit(ret)


if __name__ == "__main__":
    main()
