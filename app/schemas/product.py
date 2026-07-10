from datetime import datetime
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    temp_min_c: float = Field(2.0, ge=-20.0, le=40.0)
    temp_max_c: float = Field(8.0, ge=-20.0, le=40.0)
    max_excursion_duration_minutes: int = Field(30, ge=1)
    max_delay_hours: float = Field(24.0, ge=1.0)

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
