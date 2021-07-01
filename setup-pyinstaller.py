import argparse
import os

import PyInstaller.__main__
import toml

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()

    with open("./pyproject.toml") as t:
        pyproject = toml.load(t)

    name = pyproject["tool"]["poetry"]["name"]
    version = pyproject["tool"]["poetry"]["version"]

    if args.dev:
        flags = [
            f"--name={name}-dev",
            "--debug=imports",
            "--noconfirm",
            "--hidden-import=rasterio._shim",
            "--hidden-import=rasterio.control",
            "--hidden-import=rasterio.sample",
            "--hidden-import=rasterio.vrt",
            "--hidden-import=rasterio.rpc",
            "--hidden-import=rasterio._features",
            "--hidden-import=fiona._shim",
            "--hidden-import=fiona.schema",
            "--hidden-import=pyproj",
            "--add-data=whitebox/img/*;whitebox/img/",
            "--add-data=whitebox/WBT/whitebox_tools.exe;whitebox/",
            "--add-data=whitebox/WBT/*;whitebox/",
            "--add-data=whitebox/WBT/img/*;whitebox/WBT/img/",
            "--add-data=whitebox/testdata/*;whitebox/testdata/",
            os.path.join("pearpy/gui/", "__main__.py"),
        ]
    else:
        flags = [
            f"--name={name}-v{version}",
            "--onefile",
            "--noconfirm",
            # "--noconsole",
            # "--windowed",
            "--hidden-import=rasterio._shim",
            "--hidden-import=rasterio.control",
            "--hidden-import=rasterio.sample",
            "--hidden-import=rasterio.vrt",
            "--hidden-import=rasterio._features",
            "--hidden-import=fiona._shim",
            "--hidden-import=fiona.schema",
            "--hidden-import=pyproj",
            "--add-data=whitebox/img/*;whitebox/img/",
            "--add-data=whitebox/WBT/whitebox_tools.exe;whitebox/",
            "--add-data=whitebox/WBT/*;whitebox/",
            "--add-data=whitebox/WBT/img/*;whitebox/WBT/img/",
            "--add-data=whitebox/testdata/*;whitebox/testdata/",
            os.path.join("pearpy/gui/", "__main__.py"),
        ]
    PyInstaller.__main__.run(flags)
