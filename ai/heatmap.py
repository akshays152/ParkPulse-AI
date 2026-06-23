"""Parking hotspot heatmap accumulation."""

from __future__ import annotations

from pathlib import Path
import logging

import cv2
import numpy as np

from ai.config.settings import AppConfig
from ai.models.entities import TrackedVehicle


class ParkingHeatmap:
    """Accumulates in-zone vehicle centers and renders hotspot overlays."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._heatmap: np.ndarray | None = None
        self._logger = logging.getLogger(__name__)

    def update(self, frame_shape: tuple[int, ...], vehicles: list[TrackedVehicle]) -> None:
        if not self._config.heatmap_enabled:
            return
        if self._heatmap is None:
            self._heatmap = np.zeros(frame_shape[:2], dtype=np.float32)
        elif self._heatmap.shape != frame_shape[:2]:
            self._logger.warning("Frame shape changed; resetting parking heatmap.")
            self._heatmap = np.zeros(frame_shape[:2], dtype=np.float32)

        self._heatmap *= self._config.heatmap_decay
        for vehicle in vehicles:
            if not vehicle.inside_no_parking_zone:
                continue
            center_x, center_y = int(vehicle.center[0]), int(vehicle.center[1])
            cv2.circle(
                self._heatmap,
                (center_x, center_y),
                self._config.heatmap_radius,
                1.0,
                thickness=-1,
            )

    def overlay(self, frame: np.ndarray) -> np.ndarray:
        if not self._config.heatmap_enabled or self._heatmap is None or self._heatmap.max() <= 0:
            return frame

        normalized = cv2.normalize(self._heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        return cv2.addWeighted(colored, self._config.heatmap_alpha, frame, 1 - self._config.heatmap_alpha, 0)

    def save(self, output_path: Path) -> None:
        if self._heatmap is None or self._heatmap.max() <= 0:
            return
        output_path.parent.mkdir(parents=True, exist_ok=True)
        normalized = cv2.normalize(self._heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        cv2.imwrite(str(output_path), cv2.applyColorMap(normalized, cv2.COLORMAP_JET))
