import multiprocessing
import os
import sys
from pathlib import Path

from pearpy.gui.app import main

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    bundle_dir = Path(sys._MEIPASS)
    proj_lib = bundle_dir.joinpath("pyproj/proj_dir/share/proj")
    os.environ["PROJ_LIB"] = str(proj_lib.absolute())
    if not proj_lib.exists():
        print("ga ada bro")
        print("proj_lib")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
