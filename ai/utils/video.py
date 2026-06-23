"""Video IO helpers."""

from __future__ import annotations

from pathlib import Path

import cv2


def sanitize_fps(raw_fps: float, fallback_fps: float) -> float:
    """Normalize invalid OpenCV FPS metadata."""

    if raw_fps <= 0 or raw_fps != raw_fps:
        return fallback_fps
    return raw_fps


def open_video_capture(source: str | int) -> cv2.VideoCapture:
    """Open a video capture and raise a useful error if it fails."""

    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open video source: {source}")
    return capture


def create_video_writer(
    output_path: Path,
    fps: float,
    frame_width: int,
    frame_height: int,
) -> cv2.VideoWriter:
    """Create an MP4 writer for annotated output."""

    if fps <= 0:
        raise ValueError("Video writer FPS must be greater than 0.")
    if frame_width <= 0 or frame_height <= 0:
        raise ValueError("Video writer frame size must be greater than 0.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (frame_width, frame_height))
    if not writer.isOpened():
        raise RuntimeError(f"Unable to create output video: {output_path}")
    return writer
