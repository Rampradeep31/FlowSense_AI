from pydantic import BaseModel, Field

class ColdBoxBase(BaseModel):
    id: str = Field(..., min_length=2, max_length=100)
    model: str = Field(..., min_length=2, max_length=100)
    age_months: int = Field(..., ge=0)
    status: str = Field("active", pattern="^(active|inactive)$")

class ColdBoxCreate(ColdBoxBase):
    pass

class ColdBoxResponse(ColdBoxBase):
    class Config:
        from_attributes = True
