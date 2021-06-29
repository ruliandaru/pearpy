from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from pearpy.starting_point2 import ProcessingData
from shapely.geometry.point import Point


@dataclass
class StartingPointModel:
    stream_vector_file: str = ""
    flow_direction: str = ""
    stream: str = ""
    earlier_dsm: str = ""
    later_dsm: str = ""
    output_file: str = ""
    max_percent_length: float = 75.0
    stream_buffer_size: float = 1.0
    starting_points: List[Tuple[Point, float]] = field(default_factory=lambda: [])
    processing_data: Optional[ProcessingData] = None

    def reset(self) -> None:
        if self.processing_data is not None:
            self.processing_data.cleanup()
        self.stream_vector_file = ""
        self.flow_direction = ""
        self.stream = ""
        self.earlier_dsm = ""
        self.later_dsm = ""
        self.output_file = ""
        self.starting_points = []
        self.processing_data = None
        self.max_percent_length = 75.0
        self.stream_buffer_size = 1.0
