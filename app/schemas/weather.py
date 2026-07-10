from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class WeatherRequest(BaseModel):
    waypoints: Optional[List[List[float]]] = Field(
        None, 
        description="List of [longitude, latitude] coordinates. Optional if route_id is provided."
    )
    route_id: Optional[int] = Field(
        None, 
        description="Database route ID to fetch waypoints from. Optional if waypoints are provided."
    )

class WeatherReadingSchema(BaseModel):
    time: datetime
    temp_c: float
    humidity_pct: float
    precipitation_mm: float

class WaypointForecastSchema(BaseModel):
    waypoint_index: int
    latitude: float
    longitude: float
    forecast: List[WeatherReadingSchema]

class WeatherForecastResponse(BaseModel):
    forecasts: List[WaypointForecastSchema]
