from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

class ExcursionDetail(BaseModel):
    start_time: datetime.datetime = Field(..., description="Start timestamp of the temperature excursion event.")
    end_time: Optional[datetime.datetime] = Field(None, description="End timestamp of the excursion event (null if currently active).")
    duration_minutes: float = Field(..., description="Duration of this specific temperature breach segment in minutes.")
    max_temperature: float = Field(..., description="Highest temperature reached during this excursion segment.")
    min_temperature: float = Field(..., description="Lowest temperature reached during this excursion segment.")

    class Config:
        from_attributes = True

class ShipmentComplianceReport(BaseModel):
    shipment_id: int
    product_name: str
    carrier_name: str
    cold_box_id: str
    total_transit_hours: float = Field(..., description="Total elapsed transit time in hours.")
    status: str = Field(..., description="Current status of the shipment.")
    excursions_count: int = Field(..., description="Number of distinct temperature excursion events.")
    excursions: List[ExcursionDetail] = Field(..., description="Detailed list of temperature breach segments.")
    compliance_status: str = Field(..., description="Overall status: 'compliant' or 'non_compliant'.")
    estimated_loss_inr: float = Field(..., description="Financial loss tracker estimation based on spoilage state.")

    class Config:
        from_attributes = True

class CarrierComplianceRanking(BaseModel):
    carrier_id: int
    carrier_name: str
    reliability_pct: float = Field(..., description="Carrier historical reliability index.")
    total_shipments: int = Field(..., description="Total shipments assigned to this carrier.")
    spoiled_shipments: int = Field(..., description="Total spoiled shipments for this carrier.")
    delayed_shipments: int = Field(..., description="Total delayed shipments for this carrier.")
    compliance_score: float = Field(..., description="Percentage of safe deliveries out of total shipments.")

    class Config:
        from_attributes = True

class MonthlyComplianceSummary(BaseModel):
    total_shipments_dispatched: int = Field(..., description="Total shipments processed.")
    safe_deliveries: int = Field(..., description="Number of shipments delivered in-bound and compliant.")
    delayed_deliveries: int = Field(..., description="Number of shipments marked as delayed.")
    spoiled_deliveries: int = Field(..., description="Number of shipments spoiled by thermal breaches.")
    total_financial_loss_inr: float = Field(..., description="Estimated cumulative financial losses in INR.")
    carrier_rankings: List[CarrierComplianceRanking] = Field(..., description="Ranked list of carrier compliance indices.")

    class Config:
        from_attributes = True
