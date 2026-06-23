"""OpenCV visualization for ParkPulse AI."""

from __future__ import annotations

import cv2
import numpy as np

from ai.config.settings import AppConfig, Color
from ai.congestion_score import ScoreResult
from ai.models.entities import TrackedVehicle


class Visualizer:
    """Draws zones, boxes, IDs, durations, scores, and priority colors."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def draw(
        self,
        frame: np.ndarray,
        vehicles: list[TrackedVehicle],
        scores: dict[int, ScoreResult],
        zone_points: list[tuple[int, int]],
        fps: float | None = None,
    ) -> np.ndarray:
        output = frame.copy()
        self._draw_zone(output, zone_points)

        for vehicle in vehicles:
            score = scores.get(vehicle.track_id)
            priority = score.priority if score else "Low"
            color = self._config.priority_colors.get(priority, self._config.default_box_color)
            if not vehicle.illegal_parking:
                color = self._config.default_box_color

            x1, y1, x2, y2 = vehicle.bbox
            cv2.rectangle(output, (x1, y1), (x2, y2), color, self._config.box_thickness)
            label = self._label(vehicle, score)
            label_y = max(y1 - self._config.label_offset_y, self._config.label_min_y)
            self._draw_label(output, label, x1, label_y, color)

        if fps is not None:
            self._draw_label(
                output,
                f"FPS {fps:.1f}",
                self._config.fps_label_position[0],
                self._config.fps_label_position[1],
                self._config.default_box_color,
            )

        return output

    def _draw_zone(self, frame: np.ndarray, zone_points: list[tuple[int, int]]) -> None:
        points = np.array(zone_points, dtype=np.int32)
        overlay = frame.copy()
        cv2.polylines(
            frame,
            [points],
            isClosed=True,
            color=self._config.zone_color,
            thickness=self._config.box_thickness,
        )
        cv2.fillPoly(overlay, [points], color=self._config.zone_color)
        cv2.addWeighted(overlay, self._config.zone_alpha, frame, 1 - self._config.zone_alpha, 0, frame)

    @staticmethod
    def _label(vehicle: TrackedVehicle, score: ScoreResult | None) -> str:
        parts = [
            f"ID {vehicle.track_id}",
            vehicle.class_name,
            f"{vehicle.parking_duration_seconds:.1f}s",
            f"N {vehicle.nearby_vehicle_count}",
        ]
        if score:
            parts.extend([f"S {score.score}", score.priority])
        return " | ".join(parts)

    def _draw_label(
        self,
        frame: np.ndarray,
        text: str,
        x: int,
        y: int,
        color: Color,
    ) -> None:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = self._config.label_font_scale
        thickness = self._config.label_thickness
        padding = self._config.label_padding
        (width, height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        frame_height, frame_width = frame.shape[:2]
        x = max(0, min(x, max(frame_width - width - padding * 2, 0)))
        y = max(height + baseline, min(y, frame_height - padding - 1))
        cv2.rectangle(
            frame,
            (x, y - height - baseline),
            (x + width + padding * 2, y + padding + 1),
            color,
            -1,
        )
        cv2.putText(
            frame,
            text,
            (x + padding, y),
            font,
            font_scale,
            self._config.label_text_color,
            thickness,
            cv2.LINE_AA,
        )
