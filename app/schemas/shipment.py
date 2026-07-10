from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.product import ProductResponse
from app.schemas.cold_box import ColdBoxResponse
from app.schemas.carrier import CarrierResponse
from app.schemas.route import RouteResponse

class ShipmentBase(BaseModel):
    origin: str = Field(..., min_length=2, max_length=100)
    destination: str = Field(..., min_length=2, max_length=100)
    product_id: int
    quantity: int = Field(..., ge=1)
    cold_box_id: str
    carrier_id: int
    departure_time: datetime

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentResponse(ShipmentBase):
    id: int
    status: str
    route_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class ShipmentDetailResponse(ShipmentResponse):
    product: ProductResponse
    cold_box: ColdBoxResponse
    carrier: CarrierResponse
    route: Optional[RouteResponse] = None

    class Config:
        from_attributes = True
