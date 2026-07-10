from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

class RouteRequest(BaseModel):
    waypoints: List[List[float]] = Field(
        ..., 
        description="List of [longitude, latitude] coordinates. Minimum 2 waypoints.",
        min_length=2
    )

class RouteResponse(BaseModel):
    id: int
    waypoints: List[List[float]]
    distance_km: float
    duration_hours: float
    geometry: str
    created_at: datetime

    class Config:
        from_attributes = True
