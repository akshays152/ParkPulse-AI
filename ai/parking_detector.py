"""No-parking-zone state management and illegal parking detection."""

from __future__ import annotations

from dataclasses import dataclass

from shapely.geometry import Point, Polygon

from ai.config.settings import AppConfig
from ai.models.entities import TrackedVehicle


@dataclass(slots=True)
class ParkingState:
    """Mutable parking state for a tracked object."""

    inside_seconds: float = 0.0
    last_seen_frame: int = 0


class ParkingDetector:
    """Tracks how long vehicles remain inside configured no-parking polygons."""

    def __init__(self, config: AppConfig) -> None:
        if len(config.no_parking_zone) < 3:
            raise ValueError("No-parking zone must contain at least three points.")
        self._config = config
        self._zone = Polygon(config.no_parking_zone)
        if not self._zone.is_valid:
            raise ValueError("No-parking zone polygon is invalid.")
        self._states: dict[int, ParkingState] = {}

    @property
    def zone_points(self) -> list[tuple[int, int]]:
        return list(self._config.no_parking_zone)

    def update(self, vehicles: list[TrackedVehicle], delta_seconds: float, frame_index: int) -> None:
        active_ids = {vehicle.track_id for vehicle in vehicles}
        for vehicle in vehicles:
            anchor = vehicle.bottom_center if self._config.parking_anchor == "bottom_center" else vehicle.center
            inside = self._zone.covers(Point(anchor))
            vehicle.inside_no_parking_zone = inside

            state = self._states.setdefault(vehicle.track_id, ParkingState())
            state.last_seen_frame = frame_index

            if inside:
                state.inside_seconds += delta_seconds
            else:
                state.inside_seconds = 0.0

            vehicle.parking_duration_seconds = state.inside_seconds
            vehicle.illegal_parking = state.inside_seconds > self._config.illegal_parking_seconds

        self._drop_stale_states(active_ids, frame_index)

    def _drop_stale_states(self, active_ids: set[int], frame_index: int) -> None:
        stale_ids = [
            track_id
            for track_id, state in self._states.items()
            if track_id not in active_ids
            and frame_index - state.last_seen_frame > self._config.stale_track_frames
        ]
        for track_id in stale_ids:
            self._states.pop(track_id, None)
