from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class SensorSimulateRequest(BaseModel):
    cold_box_id: str = Field(..., description="Unique identifier for the cold box container.")
    shipment_id: Optional[str] = Field(None, description="Optional associated shipment ID.")
    failing: bool = Field(False, description="Set to true to simulate a compressor failure spike to 15°C.")
    duration_minutes: int = Field(180, description="Total history duration to simulate in minutes.", ge=5, le=1440)
    interval_minutes: int = Field(5, description="Frequency of logs in minutes.", ge=1, le=60)

class SensorReadingSchema(BaseModel):
    id: int
    cold_box_id: str
    shipment_id: Optional[str]
    temperature_c: float
    humidity_pct: float
    timestamp: datetime

    class Config:
        from_attributes = True

class SensorSimulateResponse(BaseModel):
    readings: List[SensorReadingSchema]
