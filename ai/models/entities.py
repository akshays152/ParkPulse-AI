"""Domain entities used by the AI pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


BBox = tuple[int, int, int, int]
Point = tuple[float, float]


@dataclass(slots=True)
class TrackedVehicle:
    """A vehicle detection associated with a persistent tracker ID."""

    track_id: int
    class_name: str
    bbox: BBox
    confidence: float
    center: Point
    inside_no_parking_zone: bool = False
    parking_duration_seconds: float = 0.0
    illegal_parking: bool = False
    nearby_vehicle_count: int = 0

    @property
    def bottom_center(self) -> Point:
        x1, _, x2, y2 = self.bbox
        return (x1 + x2) / 2, float(y2)


@dataclass(slots=True)
class IllegalParkingEvent:
    """Serializable illegal parking event."""

    violation_id: str
    track_id: int
    class_name: str
    duration: float
    score: int
    priority: str
    bbox: BBox
    nearby_vehicle_count: int
    started_frame_index: int
    frame_index: int
    timestamp_seconds: float
    screenshot_path: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "id": self.track_id,
            "class": self.class_name,
            "duration": round(self.duration, 2),
            "score": self.score,
            "priority": self.priority,
            "bbox": list(self.bbox),
            "nearby_vehicle_count": self.nearby_vehicle_count,
            "started_frame_index": self.started_frame_index,
            "frame_index": self.frame_index,
            "timestamp_seconds": round(self.timestamp_seconds, 2),
            "screenshot_path": self.screenshot_path,
        }
