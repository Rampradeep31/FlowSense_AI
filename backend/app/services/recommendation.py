from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Tuple
from fastapi import HTTPException
from backend.app.models import Supplier, Recommendation, PredictionHistory
from backend.app.schemas import PredictionCreate, RecommendationResponse, SupplierComparison, RecommendationCard
from backend.app.services.prediction import PredictionService

class RecommendationService:
    @staticmethod
    def calculate_risk_score(quality_rating: float, late_deliveries: int, experience: int) -> Tuple[float, str]:
        """
        Calculate Supplier Risk Score (0-100) and Level.
        Formula:
        Quality Penalty: (5.0 - Quality Rating) * 10
        Late Delivery Penalty: Late Deliveries * 4 (Capped at 40)
        Experience Discount: Experience * 2 (Capped at 20)
        Risk Score = Quality Penalty + Late Delivery Penalty - Experience Discount (Clipped to 0-100)
        """
        quality_penalty = (5.0 - quality_rating) * 10.0
        late_penalty = min(40.0, late_deliveries * 4.0)
        experience_discount = min(20.0, experience * 2.0)
        
        risk_score = quality_penalty + late_penalty - experience_discount
        risk_score = max(0.0, min(100.0, risk_score))
        
        if risk_score < 30.0:
            level = "Low"
        elif risk_score < 60.0:
            level = "Medium"
        else:
            level = "High"
            
        return round(risk_score, 2), level

    @classmethod
    def get_recommendation(
        cls,
        db: Session,
        user_id: Optional[int],
        product_name: str,
        prediction_data: PredictionCreate
    ) -> RecommendationResponse:
        """
        1. Predicts the freight cost for the specified route.
        2. Queries suppliers providing the requested product.
        3. Calculates risk premium and total landed cost.
        4. Identifies the best supplier and saves the recommendation.
        5. Returns structured comparison and recommendation breakdown.
        """
        # 1. Run prediction service
        db_prediction = PredictionService.predict_freight(db, user_id, prediction_data)
        freight_cost = db_prediction.predicted_freight_cost
        
        # 2. Get suppliers matching product
        suppliers = db.query(Supplier).filter(Supplier.product_name.ilike(product_name)).all()
        if not suppliers:
            raise HTTPException(
                status_code=404, 
                detail=f"No suppliers found offering product '{product_name}'"
            )
            
        # 3. Calculate Landed Costs for all candidates
        comparison_list: List[SupplierComparison] = []
        
        for s in suppliers:
            risk_score, risk_level = cls.calculate_risk_score(
                s.quality_rating, s.late_deliveries, s.experience
            )
            
            # Risk premium: 20% of product cost * (risk_score / 100)
            risk_premium = round(s.product_cost * (risk_score / 100.0) * 0.2, 2)
            
            total_landed_cost = round(s.product_cost + freight_cost + risk_premium, 2)
            
            comparison_list.append(SupplierComparison(
                supplier_id=s.id,
                supplier_name=s.name,
                country=s.country,
                product_cost=s.product_cost,
                predicted_freight_cost=freight_cost,
                risk_score=risk_score,
                risk_level=risk_level,
                risk_premium=risk_premium,
                total_landed_cost=total_landed_cost,
                delivery_time=s.delivery_time,
                quality_rating=s.quality_rating,
                experience=s.experience
            ))
            
        # 4. Sort suppliers by total landed cost (ascending)
        comparison_list.sort(key=lambda x: x.total_landed_cost)
        
        best_candidate = comparison_list[0]
        
        # Calculate savings vs average
        total_costs = [c.total_landed_cost for c in comparison_list]
        avg_cost = sum(total_costs) / len(total_costs)
        savings = round(max(0.0, avg_cost - best_candidate.total_landed_cost), 2)
        
        # Retrieve best supplier full details for contact info
        best_supplier_db = db.query(Supplier).filter(Supplier.id == best_candidate.supplier_id).first()
        
        # 5. Log Recommendation to database
        db_recommendation = Recommendation(
            user_id=user_id,
            prediction_id=db_prediction.id,
            recommended_supplier_id=best_candidate.supplier_id,
            total_landed_cost=best_candidate.total_landed_cost,
            product_cost=best_candidate.product_cost,
            predicted_freight_cost=freight_cost,
            risk_premium=best_candidate.risk_premium
        )
        db.add(db_recommendation)
        db.commit()
        db.refresh(db_recommendation)
        
        # 6. Build response
        card = RecommendationCard(
            recommended_supplier_name=best_candidate.supplier_name,
            country=best_candidate.country,
            product_cost=best_candidate.product_cost,
            predicted_freight_cost=freight_cost,
            risk_premium=best_candidate.risk_premium,
            total_landed_cost=best_candidate.total_landed_cost,
            savings_vs_average=savings,
            contact_info=best_supplier_db.contact_info if best_supplier_db else "N/A"
        )
        
        # Pie chart cost breakdown for the recommended supplier
        cost_breakdown = [
            {"name": "Product Cost", "value": best_candidate.product_cost},
            {"name": "Predicted Freight Cost", "value": freight_cost},
            {"name": "Risk Premium", "value": best_candidate.risk_premium}
        ]
        
        return RecommendationResponse(
            recommendation_card=card,
            cost_breakdown=cost_breakdown,
            comparison_table=comparison_list
        )
