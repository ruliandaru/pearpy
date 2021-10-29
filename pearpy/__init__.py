"""
Pearpy is an advanced version laharzpy which is standalone and has automatic volume finder.
Pearpy can do:
    1. surface hidrology generator
    2. generate lahar inundation area using confidence limit
    3. lahar generated can be vector or raster
"""

__version__ = "0.1.0"

from pearpy.distal_inundation import batch_lahar_inundation
from pearpy.starting_point import find_starting_points

__all__ = ["find_starting_points", "batch_lahar_inundation"]
