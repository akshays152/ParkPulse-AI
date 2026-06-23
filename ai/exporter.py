"""Violation artifact export: screenshots, CSV, and JSON."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

import cv2
import numpy as np

from ai.config.settings import AppConfig
from ai.models.entities import IllegalParkingEvent


class ViolationExporter:
    """Persists hackathon-demo artifacts for detected violations."""

    CSV_FIELDS = [
        "violation_id",
        "id",
        "class",
        "duration",
        "score",
        "priority",
        "nearby_vehicle_count",
        "started_frame_index",
        "frame_index",
        "timestamp_seconds",
        "bbox",
        "screenshot_path",
    ]

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._screenshot_ids: set[int] = set()
        self._logger = logging.getLogger(__name__)

    def save_screenshot(
        self,
        event: IllegalParkingEvent,
        frame: np.ndarray,
    ) -> IllegalParkingEvent:
        if not self._config.save_violation_screenshots or event.violation_id in self._screenshot_ids:
            return event

        self._config.screenshot_dir.mkdir(parents=True, exist_ok=True)
        path = self._config.screenshot_dir / f"violation_{event.violation_id}_frame_{event.frame_index}.jpg"
        if not cv2.imwrite(str(path), frame):
            self._logger.error("Failed to save violation screenshot: %s", path)
            return event
        self._screenshot_ids.add(event.violation_id)
        event.screenshot_path = str(path)
        return event

    def export_json(self, events: list[IllegalParkingEvent], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                [event.to_json() for event in sorted(events, key=lambda item: item.violation_id)],
                indent=2,
            ),
            encoding="utf-8",
        )

    def export_csv(self, events: list[IllegalParkingEvent], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
            for event in sorted(events, key=lambda item: item.violation_id):
                row = event.to_json()
                row["bbox"] = json.dumps(row["bbox"])
                writer.writerow(row)
