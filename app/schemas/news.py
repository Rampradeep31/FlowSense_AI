from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class NewsRequest(BaseModel):
    waypoints: Optional[List[List[float]]] = Field(
        None, 
        description="List of [longitude, latitude] coordinates. Optional if route_id is provided."
    )
    route_id: Optional[int] = Field(
        None, 
        description="Database route ID to fetch waypoints from. Optional if waypoints are provided."
    )
    radius_km: float = Field(
        50.0, 
        description="Proximity radius in kilometers around the route waypoints.",
        ge=0.0
    )

class NewsDisruptionSchema(BaseModel):
    title: str
    description: Optional[str]
    source: Optional[str]
    url: Optional[str]
    latitude: float
    longitude: float
    severity: str
    published_at: datetime
    distance_from_route_km: Optional[float] = None

class NewsDisruptionResponse(BaseModel):
    disruptions: List[NewsDisruptionSchema]
