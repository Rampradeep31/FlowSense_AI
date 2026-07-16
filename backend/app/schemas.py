from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
import datetime

# ==========================================
# USER SCHEMAS (Authentication)
# ==========================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# ==========================================
# SUPPLIER SCHEMAS
# ==========================================

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)
    product_name: str = Field(..., min_length=1)
    product_cost: float = Field(..., gt=0)
    delivery_time: int = Field(..., ge=0, description="Average delivery time in days")
    quality_rating: float = Field(..., ge=1.0, le=5.0, description="Quality rating from 1.0 to 5.0")
    late_deliveries: int = Field(..., ge=0, description="Number of late deliveries")
    experience: int = Field(..., ge=0, description="Years of industry experience")
    contact_info: str = Field(..., min_length=1)

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    product_name: Optional[str] = None
    product_cost: Optional[float] = None
    delivery_time: Optional[int] = None
    quality_rating: Optional[float] = None
    late_deliveries: Optional[int] = None
    experience: Optional[int] = None
    contact_info: Optional[str] = None

class SupplierOut(SupplierBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# FREIGHT PREDICTION SCHEMAS
# ==========================================

class PredictionCreate(BaseModel):
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    distance: float = Field(..., gt=0)
    fuel_price: float = Field(..., gt=0)
    month: str = Field(..., min_length=3)

class PredictionOut(PredictionCreate):
    id: int
    predicted_freight_cost: float
    confidence_score: float
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# RECOMMENDATION SCHEMAS
# ==========================================

class SupplierComparison(BaseModel):
    supplier_id: int
    supplier_name: str
    country: str
    product_cost: float
    predicted_freight_cost: float
    risk_score: float
    risk_level: str
    risk_premium: float
    total_landed_cost: float
    delivery_time: int
    quality_rating: float
    experience: int

class RecommendationCard(BaseModel):
    recommended_supplier_name: str
    country: str
    product_cost: float
    predicted_freight_cost: float
    risk_premium: float
    total_landed_cost: float
    savings_vs_average: float
    contact_info: str

class RecommendationResponse(BaseModel):
    recommendation_card: RecommendationCard
    cost_breakdown: List[dict] # For chart visualization: {"name": "Product Cost", "value": X}
    comparison_table: List[SupplierComparison]


# ==========================================
# HISTORY SCHEMAS
# ==========================================

class RecommendationOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    prediction_id: int
    recommended_supplier_id: int
    total_landed_cost: float
    product_cost: float
    predicted_freight_cost: float
    risk_premium: float
    created_at: datetime.datetime
    
    # Nested info
    prediction: Optional[PredictionOut] = None
    supplier: Optional[SupplierOut] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# DASHBOARD SCHEMAS
# ==========================================

class DashboardSummary(BaseModel):
    total_suppliers: int
    total_predictions: int
    avg_freight_cost: float
    avg_risk_score: float
    recommended_supplier: Optional[str] = "N/A"

class RecentActivity(BaseModel):
    id: int
    action: str
    timestamp: datetime.datetime

class MonthlyFreightChartData(BaseModel):
    month: str
    avg_predicted_cost: float

class SupplierRiskChartData(BaseModel):
    risk_level: str
    count: int

class DashboardResponse(BaseModel):
    summary: DashboardSummary
    recent_activities: List[RecentActivity]
    freight_chart: List[MonthlyFreightChartData]
    risk_chart: List[SupplierRiskChartData]
    top_suppliers: List[SupplierOut]
