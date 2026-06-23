# ParkPulse AI

AI-powered parking intelligence module for detecting illegally parked vehicles in CCTV video and estimating congestion impact.

## Features

- YOLOv11 vehicle detection for `car`, `motorcycle`, `bus`, and `truck`
- ByteTrack tracking with persistent vehicle IDs
- Polygon-based no-parking-zone checks using Shapely
- Per-vehicle parking timers with illegal parking threshold
- Rule-based congestion impact score from duration, nearby vehicles, and road importance
- Nearby vehicle counts within a configurable pixel radius
- Parking hotspot heatmap overlay and final heatmap export
- Smooth tracking with tuned ByteTrack settings and per-ID box smoothing
- FPS counter and structured logging
- JSON and CSV violation exports
- Screenshot capture for every unique violation
- OpenCV visualization with bounding boxes, IDs, timers, nearby counts, scores, and priority colors

## Project Structure

```text
ai/
  config/
    bytetrack_parkpulse.yaml
    default_config.json
    loader.py
    settings.py
  models/
    entities.py
  utils/
    video.py
  congestion_score.py
  exporter.py
  heatmap.py
  main.py
  parking_detector.py
  track_smoother.py
  tracker.py
  visualizer.py
requirements.txt
README.md
```

## Setup

Use Python 3.11.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

The first run downloads `yolo11n.pt` automatically through Ultralytics if it is not already present.

FastAPI and EasyOCR are not required for this module. Add them only if you later expose an API or add license-plate OCR.

## Run

Process a video file:

```bash
python -m ai.main --source path\to\cctv.mp4
```

Process webcam or CCTV camera index:

```bash
python -m ai.main --source 0 --display
```

Set road importance:

```bash
python -m ai.main --source path\to\cctv.mp4 --road-importance 3
```

Custom outputs:

```bash
python -m ai.main --source path\to\cctv.mp4 --output-video outputs\demo.mp4 --output-json outputs\events.json --output-csv outputs\events.csv
```

Use a custom config:

```bash
python -m ai.main --source path\to\cctv.mp4 --config ai\config\default_config.json
```

Default artifacts:

- Annotated video: `outputs/annotated_output.mp4`
- Violations JSON: `outputs/illegal_parking_events.json`
- Violations CSV: `outputs/illegal_parking_events.csv`
- Violation screenshots: `outputs/violation_screenshots/`
- Heatmap image: `outputs/parking_hotspots_heatmap.jpg`
- Log file: `outputs/parkpulse_ai.log`

## JSON Output

Each illegal parking event is emitted in this shape:

```json
{
  "violation_id": "12-940",
  "id": 12,
  "class": "car",
  "duration": 35,
  "score": 91,
  "priority": "High",
  "bbox": [120, 140, 260, 300],
  "nearby_vehicle_count": 4,
  "started_frame_index": 940,
  "frame_index": 940,
  "timestamp_seconds": 31.33,
  "screenshot_path": "outputs/violation_screenshots/violation_12-940_frame_940.jpg"
}
```

## Configuration

Edit `ai/config/default_config.json` to tune demo behavior without touching code:

- `no_parking_zone`
- `illegal_parking_seconds`
- `confidence_threshold`
- `iou_threshold`
- `nearby_distance_pixels`
- `parking_anchor`
- `process_every_n_frames`
- `image_size`
- `max_detections`
- `smoothing_alpha`
- `heatmap_radius`
- `heatmap_decay`
- score normalization caps

Default no-parking zone:

```json
"no_parking_zone": [[100, 120], [500, 120], [500, 450], [100, 450]]
```

## Congestion Score

The score is deterministic and does not use machine learning:

```text
score = 0.5 * parking_duration_seconds + 0.3 * nearby_vehicle_count + 0.2 * road_importance
```

The implementation normalizes each component to produce a 0-100 score:

- Parking duration is capped by `max_duration_for_score`
- Nearby count is capped by `max_nearby_vehicles_for_score`
- Road importance is normalized from 1-3

Priority:

- `0-30`: Low
- `31-70`: Medium
- `71-100`: High

## Notes

- Ultralytics uses ByteTrack through `model.track(..., tracker="ai/config/bytetrack_parkpulse.yaml")`.
- The illegal parking timer resets when a tracked vehicle leaves the polygon.
- Events are keyed by `violation_id`, while `id` remains the ByteTrack vehicle ID.
- Repeated illegal stops by the same track are exported as separate violation episodes.
- For faster realtime demos, increase `process_every_n_frames`, reduce `image_size`, or run with GPU and `use_half_precision`.
