from fastapi import APIRouter
import json, os
from typing import List
from schemas import Violation

router = APIRouter()
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "violations.json")

@router.get("/violations", response_model=List[Violation])
def get_violations():
    if not os.path.exists(DATA_PATH): return []
    with open(DATA_PATH, "r") as f: violations = json.load(f)
    
    processed = []
    for v in violations:
        score = round((v["duration"] * 0.5) + (v["impact"] * 0.3) + (v["lane_importance"] * 10 * 0.2), 1)
        severity = "Critical" if score > 35 else ("High" if score > 20 else "Medium")
        processed.append({**v, "score": score, "severity": severity})
    return sorted(processed, key=lambda x: x["score"], reverse=True)
