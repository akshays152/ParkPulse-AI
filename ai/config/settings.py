"""Application configuration for ParkPulse AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final


Color = tuple[int, int, int]

VEHICLE_CLASS_IDS: Final[set[int]] = {
    2,  # car
    3,  # motorcycle
    5,  # bus
    7,  # truck
}

NO_PARKING_ZONE: Final[list[tuple[int, int]]] = [
    (100, 120),
    (500, 120),
    (500, 450),
    (100, 450),
]

PRIORITY_COLORS: Final[dict[str, Color]] = {
    "Low": (0, 180, 0),
    "Medium": (0, 220, 255),
    "High": (0, 0, 255),
}


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings for detection, tracking, scoring, and rendering."""

    model_path: str = "yolo11n.pt"
    confidence_threshold: float = 0.35
    iou_threshold: float = 0.5
    tracker_config: str = str(
    (Path(__file__).resolve().parent / "bytetrack_parkpulse.yaml").resolve()
)
    image_size: int = 640
    max_detections: int = 80
    device: str | None = None
    use_half_precision: bool = False
    use_model_fusion: bool = True
    no_parking_zone: list[tuple[int, int]] = field(default_factory=lambda: list(NO_PARKING_ZONE))
    parking_anchor: str = "bottom_center"
    illegal_parking_seconds: float = 20.0
    road_importance: int = 2
    nearby_distance_pixels: float = 120.0
    max_duration_for_score: float = 120.0
    max_nearby_vehicles_for_score: int = 10
    low_priority_max_score: int = 30
    medium_priority_max_score: int = 70
    stale_track_frames: int = 30
    default_fps: float = 30.0
    display_window_name: str = "ParkPulse AI"
    default_output_video: Path = Path("outputs/annotated_output.mp4")
    default_output_json: Path = Path("outputs/illegal_parking_events.json")
    default_output_csv: Path = Path("outputs/illegal_parking_events.csv")
    screenshot_dir: Path = Path("outputs/violation_screenshots")
    heatmap_output_path: Path = Path("outputs/parking_hotspots_heatmap.jpg")
    output_dir: Path = Path("outputs")
    log_level: str = "INFO"
    log_file: Path = Path("outputs/parkpulse_ai.log")
    save_violation_screenshots: bool = True
    heatmap_enabled: bool = True
    heatmap_alpha: float = 0.45
    heatmap_radius: int = 32
    heatmap_decay: float = 0.995
    smoothing_enabled: bool = True
    smoothing_alpha: float = 0.65
    process_every_n_frames: int = 1
    priority_colors: dict[str, Color] = field(default_factory=lambda: dict(PRIORITY_COLORS))
    default_box_color: Color = (255, 180, 0)
    zone_color: Color = (0, 0, 255)
    zone_alpha: float = 0.15
    box_thickness: int = 2
    label_font_scale: float = 0.5
    label_thickness: int = 1
    label_padding: int = 3
    label_min_y: int = 18
    label_offset_y: int = 8
    label_text_color: Color = (255, 255, 255)
    fps_label_position: tuple[int, int] = (12, 28)

    def __post_init__(self) -> None:
        _validate_range("confidence_threshold", self.confidence_threshold, 0.0, 1.0)
        _validate_range("iou_threshold", self.iou_threshold, 0.0, 1.0)
        _validate_range("heatmap_alpha", self.heatmap_alpha, 0.0, 1.0)
        _validate_range("heatmap_decay", self.heatmap_decay, 0.0, 1.0)
        _validate_range("smoothing_alpha", self.smoothing_alpha, 0.0, 1.0)
        _validate_positive("image_size", self.image_size)
        _validate_positive("max_detections", self.max_detections)
        _validate_positive("illegal_parking_seconds", self.illegal_parking_seconds)
        _validate_positive("nearby_distance_pixels", self.nearby_distance_pixels)
        _validate_positive("max_duration_for_score", self.max_duration_for_score)
        _validate_positive("max_nearby_vehicles_for_score", self.max_nearby_vehicles_for_score)
        _validate_positive("stale_track_frames", self.stale_track_frames)
        _validate_positive("default_fps", self.default_fps)
        _validate_positive("heatmap_radius", self.heatmap_radius)
        _validate_positive("process_every_n_frames", self.process_every_n_frames)
        if self.road_importance not in {1, 2, 3}:
            raise ValueError("road_importance must be 1, 2, or 3.")
        if self.parking_anchor not in {"center", "bottom_center"}:
            raise ValueError("parking_anchor must be either 'center' or 'bottom_center'.")
        if len(self.no_parking_zone) < 3:
            raise ValueError("no_parking_zone must contain at least three points.")
        if self.low_priority_max_score >= self.medium_priority_max_score:
            raise ValueError("low_priority_max_score must be less than medium_priority_max_score.")


def _validate_range(name: str, value: float, minimum: float, maximum: float) -> None:
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}.")


def _validate_positive(name: str, value: float | int) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0.")
