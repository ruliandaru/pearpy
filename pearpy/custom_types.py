import sys
from collections import OrderedDict
from dataclasses import dataclass

from affine import Affine
from rasterio.crs import CRS

if sys.version_info >= (3, 8):
    from typing import Any, List, Tuple, TypedDict, Union
else:
    try:
        from typing import Any, List, Tuple, Union

        from typing_extensions import TypedDict
    except ImportError:
        raise ImportError("Please install typing_extension to be able use TypedDict")


class GeoJsonGeometryDict(TypedDict):
    """Typing for geojson geometry

    Parameters
    ----------
    TypedDict : [type]
        [description]
    """
    type: str
    coordinates: List[Union[Tuple[float, float], Tuple[float, float, float]]]


class GeoJsonDict(TypedDict):
    """Typing for geojson

    Parameters
    ----------
    TypedDict : [type]
        [description]
    """
    type: str
    id: str
    properties: "OrderedDict[str, Any]"
    geometry: GeoJsonGeometryDict


class RasterioMeta(TypedDict):
    """Typing for rasterio metadata

    Parameters
    ----------
    TypedDict : [type]
        [description]
    """
    count: int
    crs: CRS
    driver: str
    dtype: str
    height: int
    interleave: str
    nodata: int
    transform: Affine
    tield: bool
    width: int


@dataclass
class GeoJsonGeometry:
    type: str
    coordinates: List[Union[Tuple[float, float], Tuple[float, float, float]]]


@dataclass
class GeoJson:
    type: str
    id: str
    properties: "OrderedDict[str, Any]"
    geometry: GeoJsonGeometry
