"""Command-line entry point for ParkPulse AI."""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

import cv2
import numpy as np

from ai.config.loader import load_config
from ai.config.settings import AppConfig
from ai.congestion_score import CongestionScorer, ScoreResult
from ai.exporter import ViolationExporter
from ai.heatmap import ParkingHeatmap
from ai.models.entities import IllegalParkingEvent, TrackedVehicle
from ai.parking_detector import ParkingDetector
from ai.track_smoother import TrackSmoother
from ai.tracker import VehicleTracker
from ai.utils.video import create_video_writer, open_video_capture, sanitize_fps
from ai.visualizer import Visualizer


class ParkPulseAI:
    """Coordinates video processing, detection, tracking, scoring, and output."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._tracker = VehicleTracker(config)
        self._smoother = TrackSmoother(config)
        self._parking_detector = ParkingDetector(config)
        self._scorer = CongestionScorer(config)
        self._heatmap = ParkingHeatmap(config)
        self._visualizer = Visualizer(config)
        self._exporter = ViolationExporter(config)
        self._logger = logging.getLogger(__name__)

    def process_video(
        self,
        source: str | int,
        output_video: Path | None = None,
        output_json: Path | None = None,
        output_csv: Path | None = None,
        display: bool = False,
    ) -> list[dict[str, object]]:
        capture = open_video_capture(source)
        writer = None
        events_by_key: dict[tuple[int, int], IllegalParkingEvent] = {}
        active_violation_starts: dict[int, int] = {}

        try:
            fps = sanitize_fps(capture.get(cv2.CAP_PROP_FPS), self._config.default_fps)
            ok, first_frame = capture.read()
            if not ok:
                raise RuntimeError(f"Video source produced no frames: {source}")
            frame_height, frame_width = first_frame.shape[:2]
            process_stride = max(self._config.process_every_n_frames, 1)
            delta_seconds = process_stride / fps

            if output_video:
                writer = create_video_writer(output_video, fps / process_stride, frame_width, frame_height)

            frame_index = 0
            measured_fps = 0.0
            last_tick = time.perf_counter()
            self._logger.info("Started processing source=%s fps=%.2f size=%sx%s", source, fps, frame_width, frame_height)
            while True:
                frame = first_frame if frame_index == 0 else None
                if frame is None:
                    ok, frame = capture.read()
                    if not ok:
                        break

                if frame_index % process_stride != 0:
                    frame_index += 1
                    continue

                vehicles = self._smoother.smooth(self._tracker.track(frame))
                self._parking_detector.update(vehicles, delta_seconds, frame_index)
                self._set_nearby_counts(vehicles)
                scores = self._score_vehicles(vehicles)
                self._heatmap.update(frame.shape, vehicles)

                now = time.perf_counter()
                measured_fps = 1.0 / max(now - last_tick, 1e-6)
                last_tick = now

                annotated = self._visualizer.draw(
                    self._heatmap.overlay(frame),
                    vehicles,
                    scores,
                    self._parking_detector.zone_points,
                    measured_fps,
                )
                self._collect_events(
                    vehicles=vehicles,
                    scores=scores,
                    events_by_key=events_by_key,
                    active_violation_starts=active_violation_starts,
                    frame_index=frame_index,
                    timestamp_seconds=frame_index / fps,
                    annotated_frame=annotated,
                )

                if writer:
                    writer.write(annotated)
                if display:
                    cv2.imshow(self._config.display_window_name, annotated)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                frame_index += 1
        finally:
            capture.release()
            if writer:
                writer.release()
            if display:
                cv2.destroyAllWindows()

        events = sorted(events_by_key.values(), key=lambda item: item.violation_id)
        if output_json:
            self._exporter.export_json(events, output_json)
        if output_csv:
            self._exporter.export_csv(events, output_csv)
        if self._config.heatmap_enabled:
            self._heatmap.save(self._config.heatmap_output_path)
        self._logger.info("Finished processing. violations=%s", len(events))
        return [event.to_json() for event in events]

    def _set_nearby_counts(self, vehicles: list[TrackedVehicle]) -> None:
        counts = self._scorer.nearby_counts(vehicles)
        for vehicle in vehicles:
            vehicle.nearby_vehicle_count = counts[vehicle.track_id]

    def _score_vehicles(self, vehicles: list[TrackedVehicle]) -> dict[int, ScoreResult]:
        scores: dict[int, ScoreResult] = {}
        for vehicle in vehicles:
            if not vehicle.illegal_parking:
                continue
            scores[vehicle.track_id] = self._scorer.score(vehicle, vehicle.nearby_vehicle_count)
        return scores

    def _collect_events(
        self,
        vehicles: list[TrackedVehicle],
        scores: dict[int, ScoreResult],
        events_by_key: dict[tuple[int, int], IllegalParkingEvent],
        active_violation_starts: dict[int, int],
        frame_index: int,
        timestamp_seconds: float,
        annotated_frame: np.ndarray,
    ) -> None:
        illegal_track_ids: set[int] = set()
        visible_track_ids = {vehicle.track_id for vehicle in vehicles}
        for vehicle in vehicles:
            score = scores.get(vehicle.track_id)
            if not vehicle.illegal_parking or score is None:
                continue
            illegal_track_ids.add(vehicle.track_id)
            started_frame_index = active_violation_starts.setdefault(vehicle.track_id, frame_index)
            event_key = (vehicle.track_id, started_frame_index)
            existing = events_by_key.get(event_key)
            event = IllegalParkingEvent(
                violation_id=f"{vehicle.track_id}-{started_frame_index}",
                track_id=vehicle.track_id,
                class_name=vehicle.class_name,
                duration=vehicle.parking_duration_seconds,
                score=score.score,
                priority=score.priority,
                bbox=vehicle.bbox,
                nearby_vehicle_count=vehicle.nearby_vehicle_count,
                started_frame_index=started_frame_index,
                frame_index=frame_index,
                timestamp_seconds=timestamp_seconds,
                screenshot_path=existing.screenshot_path if existing else None,
            )
            event = self._exporter.save_screenshot(event, annotated_frame)
            events_by_key[event_key] = event
            if existing is None:
                self._logger.warning(
                    "Violation detected id=%s class=%s duration=%.2f score=%s priority=%s",
                    event.track_id,
                    event.class_name,
                    event.duration,
                    event.score,
                    event.priority,
                )
        for track_id in list(active_violation_starts):
            if track_id not in illegal_track_ids and track_id in visible_track_ids:
                active_violation_starts.pop(track_id, None)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ParkPulse AI parking intelligence module")
    parser.add_argument("--source", required=True, help="Path to video file, camera index, or stream URL.")
    parser.add_argument("--config", default="ai/config/default_config.json", help="Path to JSON config file.")
    parser.add_argument("--output-video", help="Annotated MP4 path.")
    parser.add_argument("--output-json", help="JSON output path.")
    parser.add_argument("--output-csv", help="CSV output path.")
    parser.add_argument("--model", help="Ultralytics YOLOv11 model path.")
    parser.add_argument("--road-importance", type=int, choices=[1, 2, 3])
    parser.add_argument("--display", action="store_true", help="Display annotated frames while processing.")
    return parser.parse_args()


def parse_source(value: str) -> str | int:
    return int(value) if value.isdigit() else value


def main() -> None:
    args = parse_args()
    config = load_config(
        Path(args.config) if args.config else None,
        model_path=args.model,
        road_importance=args.road_importance,
        default_output_video=Path(args.output_video) if args.output_video else None,
        default_output_json=Path(args.output_json) if args.output_json else None,
        default_output_csv=Path(args.output_csv) if args.output_csv else None,
    )
    configure_logging(config)
    app = ParkPulseAI(config)
    events = app.process_video(
        source=parse_source(args.source),
        output_video=config.default_output_video,
        output_json=config.default_output_json,
        output_csv=config.default_output_csv,
        display=args.display,
    )
    print(json.dumps(events, indent=2))


def configure_logging(config: AppConfig) -> None:
    config.log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
        handlers=[
            logging.FileHandler(config.log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

from pathlib import Path
import time


def analyze_video(video_path: str):

    config = load_config(None)

    configure_logging(config)

    app = ParkPulseAI(config)

    output_folder = Path("backend/outputs")
    output_folder.mkdir(parents=True, exist_ok=True)

    start = time.time()

    events = app.process_video(
        source=video_path,
        output_video=output_folder / "annotated.mp4",
        output_json=output_folder / "violations.json",
        output_csv=output_folder / "violations.csv",
        display=False,
    )

    processing_time = round(time.time() - start, 2)

    high = 0
    medium = 0
    low = 0

    for event in events:
        priority = event.get("priority", "").lower()

        if priority == "high":
            high += 1
        elif priority == "medium":
            medium += 1
        else:
            low += 1

    return {
        "success": True,
        "processing_time": processing_time,
        "total_violations": len(events),
        "high_priority": high,
        "medium_priority": medium,
        "low_priority": low,
        "violations": events,
        "output_video": str(output_folder / "annotated.mp4"),
        "output_json": str(output_folder / "violations.json"),
        "output_csv": str(output_folder / "violations.csv"),
        "heatmap": str(config.heatmap_output_path),
    }

if __name__ == "__main__":
    main()
