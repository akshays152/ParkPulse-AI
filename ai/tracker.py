"""YOLOv11 vehicle detection and ByteTrack tracking adapter."""

from __future__ import annotations

import logging

import numpy as np
from ultralytics import YOLO

from ai.config.settings import AppConfig, VEHICLE_CLASS_IDS
from ai.models.entities import BBox, TrackedVehicle


class VehicleTracker:
    """Runs YOLOv11 detection with ByteTrack association."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._model = YOLO(config.model_path)
        self._logger = logging.getLogger(__name__)
        if config.use_model_fusion:
            self._fuse_model()

    def _fuse_model(self) -> None:
        try:
            self._model.fuse()
        except Exception as exc:
            self._logger.debug("Model fusion skipped: %s", exc)

    def track(self, frame: np.ndarray) -> list[TrackedVehicle]:
        kwargs = {
            "persist": True,
            "tracker": self._config.tracker_config,
            "conf": self._config.confidence_threshold,
            "iou": self._config.iou_threshold,
            "classes": list(VEHICLE_CLASS_IDS),
            "imgsz": self._config.image_size,
            "max_det": self._config.max_detections,
            "half": self._config.use_half_precision,
            "verbose": False,
        }
        if self._config.device is not None:
            kwargs["device"] = self._config.device

        try:
            results = self._model.track(frame, **kwargs)
        except Exception as exc:
            raise RuntimeError(f"Vehicle tracking failed: {exc}") from exc

        if not results:
            return []
        return list(self._parse_result(results[0]))

    @staticmethod
    def _parse_result(result: object) -> list[TrackedVehicle]:
        names = getattr(result, "names", {})
        boxes = getattr(result, "boxes", None)
        if boxes is None or boxes.id is None or boxes.xyxy is None:
            return []

        xyxy = boxes.xyxy.cpu().numpy()
        track_ids = boxes.id.cpu().numpy().astype(int)
        class_ids = boxes.cls.cpu().numpy().astype(int)
        confidences = boxes.conf.cpu().numpy()

        vehicles: list[TrackedVehicle] = []
        for bbox_array, track_id, class_id, confidence in zip(xyxy, track_ids, class_ids, confidences):
            bbox = VehicleTracker._to_bbox(bbox_array)
            x1, y1, x2, y2 = bbox
            center = ((x1 + x2) / 2, (y1 + y2) / 2)
            vehicles.append(
                TrackedVehicle(
                    track_id=int(track_id),
                    class_name=str(names.get(int(class_id), class_id)),
                    bbox=bbox,
                    confidence=float(confidence),
                    center=center,
                )
            )
        return vehicles

    @staticmethod
    def _to_bbox(values: np.ndarray) -> BBox:
        x1, y1, x2, y2 = values.astype(int).tolist()
        return int(x1), int(y1), int(x2), int(y2)
