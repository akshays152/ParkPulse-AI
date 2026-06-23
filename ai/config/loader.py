"""Config-file loader for ParkPulse AI."""

from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from typing import Any

from ai.config.settings import AppConfig


PATH_FIELDS = {
    "default_output_video",
    "default_output_json",
    "default_output_csv",
    "screenshot_dir",
    "heatmap_output_path",
    "output_dir",
    "log_file",
}


def load_config(config_path: Path | None = None, **overrides: Any) -> AppConfig:
    """Load AppConfig from JSON and apply CLI overrides."""

    data: dict[str, Any] = {}
    if config_path:
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise RuntimeError(f"Unable to read config file: {config_path}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSON config file: {config_path}") from exc

    data.update({key: value for key, value in overrides.items() if value is not None})
    valid_fields = {field.name for field in fields(AppConfig)}
    filtered = {key: _normalize_value(key, value) for key, value in data.items() if key in valid_fields}
    return AppConfig(**filtered)


def _normalize_value(key: str, value: Any) -> Any:
    if key in PATH_FIELDS and value is not None:
        return Path(value)
    if key == "no_parking_zone":
        return [(int(point[0]), int(point[1])) for point in value]
    if key == "fps_label_position":
        return (int(value[0]), int(value[1]))
    if key == "priority_colors":
        return {str(name): tuple(color) for name, color in value.items()}
    return value
