"""Lightweight track smoothing to reduce jitter and visual ID instability."""

from __future__ import annotations

from dataclasses import dataclass

from ai.config.settings import AppConfig
from ai.models.entities import BBox, TrackedVehicle


@dataclass(slots=True)
class SmoothTrackState:
    bbox: tuple[float, float, float, float]
    missed_frames: int = 0


class TrackSmoother:
    """Applies exponential moving average smoothing per tracker ID."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._states: dict[int, SmoothTrackState] = {}

    def smooth(self, vehicles: list[TrackedVehicle]) -> list[TrackedVehicle]:
        self._drop_duplicate_tracks(vehicles)
        if not self._config.smoothing_enabled:
            self._drop_stale({vehicle.track_id for vehicle in vehicles})
            return vehicles

        active_ids = {vehicle.track_id for vehicle in vehicles}
        alpha = self._config.smoothing_alpha
        for vehicle in vehicles:
            current = tuple(float(value) for value in vehicle.bbox)
            state = self._states.get(vehicle.track_id)
            if state is None:
                state = SmoothTrackState(bbox=current)
                self._states[vehicle.track_id] = state
            else:
                state.bbox = tuple(
                    alpha * current_value + (1 - alpha) * previous_value
                    for current_value, previous_value in zip(current, state.bbox)
                )
                state.missed_frames = 0

            vehicle.bbox = self._to_bbox(state.bbox)
            x1, y1, x2, y2 = vehicle.bbox
            vehicle.center = ((x1 + x2) / 2, (y1 + y2) / 2)

        self._drop_stale(active_ids)
        return vehicles

    @staticmethod
    def _drop_duplicate_tracks(vehicles: list[TrackedVehicle]) -> None:
        """Keep the highest-confidence detection if a tracker emits duplicate IDs."""

        best_by_id: dict[int, TrackedVehicle] = {}
        for vehicle in vehicles:
            current_best = best_by_id.get(vehicle.track_id)
            if current_best is None or vehicle.confidence > current_best.confidence:
                best_by_id[vehicle.track_id] = vehicle
        if len(best_by_id) == len(vehicles):
            return
        vehicles[:] = list(best_by_id.values())

    def _drop_stale(self, active_ids: set[int]) -> None:
        stale_ids: list[int] = []
        for track_id, state in self._states.items():
            if track_id in active_ids:
                continue
            state.missed_frames += 1
            if state.missed_frames > self._config.stale_track_frames:
                stale_ids.append(track_id)
        for track_id in stale_ids:
            self._states.pop(track_id, None)

    @staticmethod
    def _to_bbox(values: tuple[float, float, float, float]) -> BBox:
        x1, y1, x2, y2 = values
        return round(x1), round(y1), round(x2), round(y2)
