from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.shipment import ShipmentResponse

class AlertResponse(BaseModel):
    id: int
    shipment_id: int
    alert_type: str
    severity: str
    message: str
    why_info: Dict[str, Any]
    is_acknowledged: bool
    created_at: datetime
    shipment: Optional[ShipmentResponse] = None

    class Config:
        from_attributes = True
