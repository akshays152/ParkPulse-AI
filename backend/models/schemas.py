from pydantic import BaseModel
from typing import List

class Violation(BaseModel):
    vehicle: str
    duration: int
    impact: int
    lane_importance: int
    score: float
    severity: str
    timestamp: str

class Stats(BaseModel):
    vehicles: int
    violations: int
    critical_threats: int
    avg_score: int
    congestion_reduced: str
    clearance_time_mins: int

class DynamicRecommendation(BaseModel):
    vehicle: str
    message: str
    score: float
    severity: str
    impact_lanes: int
