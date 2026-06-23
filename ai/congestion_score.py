"""Rule-based congestion impact scoring."""

from __future__ import annotations

from dataclasses import dataclass

from ai.config.settings import AppConfig
from ai.models.entities import TrackedVehicle


@dataclass(frozen=True)
class ScoreResult:
    """Congestion score and priority classification."""

    score: int
    priority: str


class CongestionScorer:
    """Computes normalized congestion impact without machine learning."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def nearby_vehicle_count(
        self,
        target: TrackedVehicle,
        vehicles: list[TrackedVehicle],
    ) -> int:
        radius_squared = self._config.nearby_distance_pixels * self._config.nearby_distance_pixels
        count = 0
        for vehicle in vehicles:
            if vehicle.track_id == target.track_id:
                continue
            delta_x = target.center[0] - vehicle.center[0]
            delta_y = target.center[1] - vehicle.center[1]
            if delta_x * delta_x + delta_y * delta_y <= radius_squared:
                count += 1
        return count

    def nearby_counts(self, vehicles: list[TrackedVehicle]) -> dict[int, int]:
        """Compute all nearby counts in one pass over pairs."""

        counts = {vehicle.track_id: 0 for vehicle in vehicles}
        radius_squared = self._config.nearby_distance_pixels * self._config.nearby_distance_pixels
        for index, vehicle in enumerate(vehicles):
            for other in vehicles[index + 1 :]:
                delta_x = vehicle.center[0] - other.center[0]
                delta_y = vehicle.center[1] - other.center[1]
                if delta_x * delta_x + delta_y * delta_y <= radius_squared:
                    counts[vehicle.track_id] += 1
                    counts[other.track_id] += 1
        return counts

    def score(self, vehicle: TrackedVehicle, nearby_vehicle_count: int) -> ScoreResult:
        duration_component = min(
            vehicle.parking_duration_seconds / self._config.max_duration_for_score,
            1.0,
        )
        nearby_component = min(
            nearby_vehicle_count / self._config.max_nearby_vehicles_for_score,
            1.0,
        )
        road_component = min(max(self._config.road_importance, 1), 3) / 3

        normalized = (
            0.5 * duration_component
            + 0.3 * nearby_component
            + 0.2 * road_component
        ) * 100
        score = max(0, min(100, round(normalized)))
        return ScoreResult(score=score, priority=self._priority(score))

    def _priority(self, score: int) -> str:
        if score <= self._config.low_priority_max_score:
            return "Low"
        if score <= self._config.medium_priority_max_score:
            return "Medium"
        return "High"
