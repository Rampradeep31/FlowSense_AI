from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import datetime
from app.schemas.prediction import ShapExplanation

class WhatIfRequest(BaseModel):
    shipment_id: int = Field(..., description="The database ID of the shipment to simulate.")
    carrier_id: Optional[int] = Field(None, description="Simulated carrier ID option.")
    cold_box_id: Optional[str] = Field(None, description="Simulated cold box ID option.")
    departure_time: Optional[datetime.datetime] = Field(None, description="Simulated departure timestamp option.")

class WhatIfResponse(BaseModel):
    shipment_id: int
    original_delay_hours: float = Field(..., description="Nominal transit delay in hours.")
    original_spoilage_probability: float = Field(..., description="Nominal spoilage probability (0.0 to 1.0).")
    original_risk_category: str = Field(..., description="Nominal risk tier ('low', 'medium', 'high').")
    simulated_delay_hours: float = Field(..., description="Simulated transit delay in hours.")
    simulated_spoilage_probability: float = Field(..., description="Simulated spoilage probability.")
    simulated_risk_category: str = Field(..., description="Simulated risk tier.")
    delay_reduction_hours: float = Field(..., description="Hours saved by simulated options (positive is improvement).")
    spoilage_reduction_pct: float = Field(..., description="Percentage of risk reduced by simulated options (positive is improvement).")
    shap_explanations: List[ShapExplanation] = Field(..., description="SHAP value explanations for the simulated scenario.")

class OptimizationRecommendation(BaseModel):
    type: str = Field(..., description="Recommendation category: 'carrier_upgrade', 'box_upgrade', or 'departure_shift'.")
    description: str = Field(..., description="Human-readable description of recommendation.")
    predicted_delay_reduction_hours: float = Field(..., description="Hours saved by implementing this recommendation.")
    predicted_spoilage_reduction_pct: float = Field(..., description="Spoilage risk probability percentage points saved.")
    actionable_details: Dict[str, Any] = Field(..., description="Actionable database parameters (e.g. carrier_id, departure_time).")

class RecommendationResponse(BaseModel):
    shipment_id: int
    original_risk_category: str = Field(..., description="Nominal risk tier prior to optimizations.")
    recommendations: List[OptimizationRecommendation] = Field(..., description="Ranked optimization suggestions.")
