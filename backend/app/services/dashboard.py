from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import datetime
from backend.app.models import Supplier, PredictionHistory, Recommendation
from backend.app.schemas import (
    DashboardSummary, RecentActivity, MonthlyFreightChartData, 
    SupplierRiskChartData, DashboardResponse, SupplierOut
)
from backend.app.services.recommendation import RecommendationService

class DashboardService:
    @classmethod
    def get_dashboard_data(cls, db: Session) -> DashboardResponse:
        # 1. Total counts
        total_suppliers = db.query(Supplier).count()
        total_predictions = db.query(PredictionHistory).count()
        
        # 2. Average predicted freight cost
        avg_freight = db.query(func.avg(PredictionHistory.predicted_freight_cost)).scalar() or 0.0
        avg_freight = round(float(avg_freight), 2)
        
        # 3. Calculate average supplier risk score and supplier risk chart
        all_suppliers = db.query(Supplier).all()
        risk_counts = {"Low": 0, "Medium": 0, "High": 0}
        total_risk = 0.0
        
        for s in all_suppliers:
            risk_score, risk_level = RecommendationService.calculate_risk_score(
                s.quality_rating, s.late_deliveries, s.experience
            )
            total_risk += risk_score
            risk_counts[risk_level] += 1
            
        avg_risk = 0.0
        if total_suppliers > 0:
            avg_risk = round(total_risk / total_suppliers, 2)
            
        # 4. Latest recommended supplier name
        latest_rec = db.query(Recommendation).order_by(Recommendation.id.desc()).first()
        recommended_supplier_name = "N/A"
        if latest_rec and latest_rec.supplier:
            recommended_supplier_name = latest_rec.supplier.name
            
        summary = DashboardSummary(
            total_suppliers=total_suppliers,
            total_predictions=total_predictions,
            avg_freight_cost=avg_freight,
            avg_risk_score=avg_risk,
            recommended_supplier=recommended_supplier_name
        )
        
        # 5. Compile recent activities (merge and sort recent records)
        activities = []
        act_id = 1
        
        # Latest 3 suppliers
        recent_suppliers = db.query(Supplier).order_by(Supplier.id.desc()).limit(3).all()
        for s in recent_suppliers:
            activities.append(RecentActivity(
                id=act_id,
                action=f"New supplier registered: {s.name} ({s.country})",
                timestamp=s.created_at
            ))
            act_id += 1
            
        # Latest 3 predictions
        recent_preds = db.query(PredictionHistory).order_by(PredictionHistory.id.desc()).limit(3).all()
        for p in recent_preds:
            activities.append(RecentActivity(
                id=act_id,
                action=f"Freight predicted: {p.origin} to {p.destination} (Rs. {p.predicted_freight_cost})",
                timestamp=p.created_at
            ))
            act_id += 1
            
        # Latest 3 recommendations
        recent_recs = db.query(Recommendation).order_by(Recommendation.id.desc()).limit(3).all()
        for r in recent_recs:
            sup_name = r.supplier.name if r.supplier else "Unknown"
            activities.append(RecentActivity(
                id=act_id,
                action=f"Procurement recommended: {sup_name} (Landed Cost: Rs. {r.total_landed_cost})",
                timestamp=r.created_at
            ))
            act_id += 1
            
        # Sort activities by timestamp descending
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        activities = activities[:5] # Keep top 5
        
        # Adjust ID sequence for sorted list
        for idx, act in enumerate(activities):
            act.id = idx + 1
            
        # 6. Monthly Freight Chart Data
        # Group by month and calculate average predicted cost
        monthly_data = (
            db.query(PredictionHistory.month, func.avg(PredictionHistory.predicted_freight_cost))
            .group_by(PredictionHistory.month)
            .all()
        )
        
        # Sort months in calendar order if possible, or keep as is
        calendar_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        freight_chart_list = []
        
        if monthly_data:
            # Map database results
            db_month_map = {m: float(avg) for m, avg in monthly_data}
            for m_name in calendar_months:
                if m_name in db_month_map:
                    freight_chart_list.append(MonthlyFreightChartData(
                        month=m_name[:3], # Use abbreviation like Jan, Feb
                        avg_predicted_cost=round(db_month_map[m_name], 2)
                    ))
        else:
            # Fallback empty chart baseline
            for m_name in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                freight_chart_list.append(MonthlyFreightChartData(month=m_name, avg_predicted_cost=0.0))
                
        # 7. Risk Chart Data
        risk_chart_list = [
            SupplierRiskChartData(risk_level="Low", count=risk_counts["Low"]),
            SupplierRiskChartData(risk_level="Medium", count=risk_counts["Medium"]),
            SupplierRiskChartData(risk_level="High", count=risk_counts["High"])
        ]
        
        # 8. Top Suppliers (by quality rating desc, limit 5)
        top_suppliers_db = db.query(Supplier).order_by(Supplier.quality_rating.desc()).limit(5).all()
        top_suppliers = [SupplierOut.model_validate(s) for s in top_suppliers_db]
        
        return DashboardResponse(
            summary=summary,
            recent_activities=activities,
            freight_chart=freight_chart_list,
            risk_chart=risk_chart_list,
            top_suppliers=top_suppliers
        )
