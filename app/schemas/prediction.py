from pydantic import BaseModel, Field
from typing import List, Dict, Any
import datetime

class DelayPredictionRequest(BaseModel):
    shipment_id: int = Field(..., description="The database ID of the shipment to analyze.")

class ShapExplanation(BaseModel):
    feature_name: str = Field(..., description="Name of the input feature.")
    shap_value: float = Field(..., description="Computed Shapley value contribution.")
    description: str = Field(..., description="Human-readable explanation of this feature's impact.")

    class Config:
        from_attributes = True

class DelayPredictionResponse(BaseModel):
    shipment_id: int
    predicted_delay_hours: float = Field(..., description="Expected delay duration in hours.")
    delay_probability: float = Field(..., description="Estimated probability of delay (0.0 to 1.0).")
    base_value: float = Field(..., description="Base model delay prediction (nominal mean).")
    shap_explanations: List[ShapExplanation] = Field(..., description="SHAP feature importance attributions.")

    class Config:
        from_attributes = True

class SpoilagePredictionRequest(BaseModel):
    shipment_id: int = Field(..., description="The database ID of the shipment to analyze.")

class SpoilagePredictionResponse(BaseModel):
    shipment_id: int
    spoilage_probability: float = Field(..., description="Estimated probability of product spoilage (0.0 to 1.0).")
    risk_category: str = Field(..., description="Risk tier: 'low', 'medium', or 'high'.")
    base_value: float = Field(..., description="Base model spoilage probability (nominal mean).")
    shap_explanations: List[ShapExplanation] = Field(..., description="SHAP feature importance attributions.")

    class Config:
        from_attributes = True

class DemandPredictionRequest(BaseModel):
    product_id: int = Field(..., description="The database ID of the product.")
    destination: str = Field(..., description="The name of the destination clinic or hospital.")
    forecast_days: int = Field(7, ge=1, le=14, description="Number of days to forecast.")

class DemandForecastItem(BaseModel):
    date: datetime.date = Field(..., description="Forecast date.")
    quantity: int = Field(..., description="Predicted demand quantity in doses/vials.")

    class Config:
        from_attributes = True

class DemandPredictionResponse(BaseModel):
    product_id: int
    destination: str
    forecast: List[DemandForecastItem] = Field(..., description="Daily demand forecasts.")
    total_forecasted: int = Field(..., description="Sum of all daily forecasted quantities.")
    base_value: float = Field(..., description="Base model demand prediction (historical baseline mean).")
    shap_explanations: List[ShapExplanation] = Field(..., description="SHAP feature importance attributions.")

    class Config:
        from_attributes = True
