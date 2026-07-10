from pydantic import BaseModel, Field

class CarrierBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    reliability_pct: float = Field(95.0, ge=0.0, le=100.0)

class CarrierCreate(CarrierBase):
    pass

class CarrierResponse(CarrierBase):
    id: int

    class Config:
        from_attributes = True
