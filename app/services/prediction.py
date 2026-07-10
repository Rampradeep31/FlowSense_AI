import logging
import datetime
import math
import random
from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.shipment import Shipment
from app.models.product import Product
from app.models.cold_box import ColdBox
from app.models.carrier import Carrier
from app.services.weather import weather_service
from app.services.news import news_service

logger = logging.getLogger(__name__)

class PredictionService:
    async def predict_delay(self, db: AsyncSession, shipment_id: int) -> Dict[str, Any]:
        """
        Retrieves a shipment from the database and runs delay prediction.
        """
        stmt = (
            select(Shipment)
            .options(
                selectinload(Shipment.product),
                selectinload(Shipment.carrier),
                selectinload(Shipment.route)
            )
            .where(Shipment.id == shipment_id)
        )
        result = await db.execute(stmt)
        shipment = result.scalars().first()
        if not shipment:
            raise ValueError(f"Shipment with ID {shipment_id} not found.")

        return await self.predict_delay_for_shipment(db, shipment)

    async def predict_delay_for_shipment(self, db: AsyncSession, shipment: Shipment) -> Dict[str, Any]:
        """
        Predicts transit delay and probability using a pre-loaded Shipment model object.
        Used directly by What-If simulation engine.
        """
        # 1. WEATHER DELAY COMPONENT
        weather_delay = 0.0
        weather_data = []
        if shipment.route:
            try:
                weather_data = await weather_service.get_forecast(shipment.route.waypoints)
                for w in weather_data:
                    temp = w.get("temp", 25.0)
                    pop = w.get("pop", 0.0)
                    if temp > 35.0:
                        weather_delay += 0.4
                    if pop > 0.5:
                        weather_delay += 0.8
                weather_delay = min(weather_delay, 4.0)
            except Exception as e:
                logger.error(f"Weather fetch failed for delay prediction: {e}")
                weather_delay = 1.0

        # 2. NEWS DISRUPTIONS COMPONENT
        news_delay = 0.0
        if shipment.route:
            try:
                news_data = await news_service.get_disruptions(shipment.route.waypoints)
                for item in news_data:
                    severity = item.get("severity", "info").lower()
                    if severity == "critical":
                        news_delay += 3.0
                    elif severity == "warning":
                        news_delay += 1.5
                    else:
                        news_delay += 0.5
                news_delay = min(news_delay, 6.0)
            except Exception as e:
                logger.error(f"News fetch failed for delay prediction: {e}")
                news_delay = 0.0

        # 3. CARRIER RELIABILITY COMPONENT
        carrier_reliability = shipment.carrier.reliability_pct if shipment.carrier else 95.0
        carrier_delay = max(0.0, (100.0 - carrier_reliability) / 8.0)

        # 4. INTERACTION TERM
        interaction = weather_delay * carrier_delay * 0.15

        # 5. SHAP CALCULATOR (3-Feature Game)
        base_value = 0.5

        W = weather_delay
        N = news_delay
        C = carrier_delay
        I = interaction

        # v(S)
        v_empty = base_value
        v_1 = base_value + W
        v_2 = base_value + N
        v_3 = base_value + C
        v_12 = base_value + W + N
        v_13 = base_value + W + C + I
        v_23 = base_value + N + C
        v_123 = base_value + W + N + C + I

        # Shapley Values
        shap_weather = W + 0.5 * I
        shap_news = N
        shap_carrier = C + 0.5 * I

        # Verify efficiency property
        total_effect = v_123 - v_empty
        assert abs((shap_weather + shap_news + shap_carrier) - total_effect) < 1e-5

        predicted_delay_hours = v_123
        delay_probability = 1.0 / (1.0 + math.exp(-(predicted_delay_hours - 2.0) / 1.5))

        return {
            "shipment_id": shipment.id or 0,
            "predicted_delay_hours": round(predicted_delay_hours, 2),
            "delay_probability": round(delay_probability, 3),
            "base_value": base_value,
            "shap_explanations": [
                {
                    "feature_name": "weather_conditions",
                    "shap_value": round(shap_weather, 2),
                    "description": f"Weather along the route waypoints adds {round(shap_weather, 1)}h to the expected delay."
                },
                {
                    "feature_name": "news_disruptions",
                    "shap_value": round(shap_news, 2),
                    "description": f"Active regional highway accidents or closures add {round(shap_news, 1)}h to the expected delay."
                },
                {
                    "feature_name": "carrier_reliability",
                    "shap_value": round(shap_carrier, 2),
                    "description": f"Carrier historical performance and reliability rate of {carrier_reliability}% adds {round(shap_carrier, 1)}h of delay risk."
                }
            ]
        }

    async def predict_spoilage(self, db: AsyncSession, shipment_id: int) -> Dict[str, Any]:
        """
        Retrieves a shipment from the database and runs spoilage prediction.
        """
        stmt = (
            select(Shipment)
            .options(
                selectinload(Shipment.cold_box),
                selectinload(Shipment.route),
                selectinload(Shipment.carrier)
            )
            .where(Shipment.id == shipment_id)
        )
        result = await db.execute(stmt)
        shipment = result.scalars().first()
        if not shipment:
            raise ValueError(f"Shipment with ID {shipment_id} not found.")

        delay_pred = await self.predict_delay_for_shipment(db, shipment)
        return await self.predict_spoilage_for_shipment(db, shipment, delay_pred["predicted_delay_hours"])

    async def predict_spoilage_for_shipment(self, db: AsyncSession, shipment: Shipment, predicted_delay: float) -> Dict[str, Any]:
        """
        Predicts product spoilage risk using a pre-loaded Shipment model object.
        Used directly by What-If simulation engine.
        """
        # 1. BOX QUALITY COEFFICIENT
        box_age = shipment.cold_box.age_months if shipment.cold_box else 12.0
        box_impact = (box_age / 24.0) * 0.8

        # 2. TEMP EXPOSURE COEFFICIENT
        max_temp = 25.0
        if shipment.route:
            try:
                weather_data = await weather_service.get_forecast(shipment.route.waypoints)
                if weather_data:
                    max_temp = max(w.get("temp", 25.0) for w in weather_data)
            except Exception:
                pass
        temp_impact = max(0.0, max_temp - 25.0) * 0.18

        # 3. TRANSIT DELAY COEFFICIENT
        delay_impact = predicted_delay * 0.35

        # 4. LOGISTIC FUNCTION EVALUATIONS FOR COMBINATORIAL SHAP
        z_0 = -3.0

        def v(S_set: set) -> float:
            score = z_0
            if 1 in S_set:
                score += box_impact
            if 2 in S_set:
                score += temp_impact
            if 3 in S_set:
                score += delay_impact
            return 1.0 / (1.0 + math.exp(-score))

        v_empty = v(set())
        v_1 = v({1})
        v_2 = v({2})
        v_3 = v({3})
        v_12 = v({1, 2})
        v_13 = v({1, 3})
        v_23 = v({2, 3})
        v_123 = v({1, 2, 3})

        # Shapley Calculation
        shap_box = (
            (1/3) * (v_1 - v_empty) +
            (1/6) * ((v_12 - v_2) + (v_13 - v_3)) +
            (1/3) * (v_123 - v_23)
        )
        shap_temp = (
            (1/3) * (v_2 - v_empty) +
            (1/6) * ((v_12 - v_1) + (v_23 - v_3)) +
            (1/3) * (v_123 - v_13)
        )
        shap_delay = (
            (1/3) * (v_3 - v_empty) +
            (1/6) * ((v_13 - v_1) + (v_23 - v_2)) +
            (1/3) * (v_123 - v_12)
        )

        total_effect = v_123 - v_empty
        assert abs((shap_box + shap_temp + shap_delay) - total_effect) < 1e-5

        spoilage_probability = v_123

        if spoilage_probability < 0.12:
            risk_category = "low"
        elif spoilage_probability < 0.35:
            risk_category = "medium"
        else:
            risk_category = "high"

        return {
            "shipment_id": shipment.id or 0,
            "spoilage_probability": round(spoilage_probability, 3),
            "risk_category": risk_category,
            "base_value": round(v_empty, 4),
            "shap_explanations": [
                {
                    "feature_name": "box_quality",
                    "shap_value": round(shap_box, 4),
                    "description": f"Cold box degradation (age: {box_age} months) changes spoilage risk by {round(shap_box * 100, 1)}%."
                },
                {
                    "feature_name": "temperature_exposure",
                    "shap_value": round(shap_temp, 4),
                    "description": f"Forecasted maximum ambient heat exposure of {round(max_temp, 1)}°C changes spoilage risk by {round(shap_temp * 100, 1)}%."
                },
                {
                    "feature_name": "transit_delay",
                    "shap_value": round(shap_delay, 4),
                    "description": f"Estimated transit delay of {round(predicted_delay, 1)}h increases thermal load duration, changing risk by {round(shap_delay * 100, 1)}%."
                }
            ]
        }

    async def forecast_demand(self, db: AsyncSession, product_id: int, destination: str, forecast_days: int) -> Dict[str, Any]:
        """
        Forecasts daily demand at a destination clinic/hospital.
        """
        product = (await db.execute(select(Product).where(Product.id == product_id))).scalars().first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found.")

        historical_baseline = 120.0
        today = datetime.date.today()
        forecast_items = []
        total_forecasted = 0
        total_shap_weather = 0.0
        total_shap_seasonality = 0.0

        from app.api.endpoints.shipment import geocode_city
        coords = geocode_city(destination)

        weather_forecast = []
        try:
            weather_forecast = await weather_service.get_forecast([coords])
        except Exception:
            pass

        for d in range(forecast_days):
            target_date = today + datetime.timedelta(days=d)
            month = target_date.month
            if month in [6, 7, 8, 9]:
                seasonality_factor = 0.25
            elif month in [11, 12, 1]:
                seasonality_factor = 0.12
            else:
                seasonality_factor = 0.0

            weather_turnout_impact = 0.0
            if d < len(weather_forecast):
                w_day = weather_forecast[d]
                pop = w_day.get("pop", 0.0)
                temp = w_day.get("temp", 25.0)
                if pop > 0.6:
                    weather_turnout_impact = -0.15
                elif temp > 38.0:
                    weather_turnout_impact = -0.10
                elif 20.0 <= temp <= 28.0:
                    weather_turnout_impact = 0.05
            else:
                if month in [6, 7, 8, 9] and random.random() < 0.4:
                    weather_turnout_impact = -0.15

            H = historical_baseline
            W = weather_turnout_impact
            M = seasonality_factor

            shap_weather_day = H * W + 0.5 * H * W * M
            shap_seasonality_day = H * M + 0.5 * H * W * M

            predicted_qty = max(10, int(H + shap_weather_day + shap_seasonality_day))
            forecast_items.append({
                "date": target_date,
                "quantity": predicted_qty
            })
            total_forecasted += predicted_qty
            total_shap_weather += shap_weather_day
            total_shap_seasonality += shap_seasonality_day

        base_value_total = historical_baseline * forecast_days

        return {
            "product_id": product_id,
            "destination": destination,
            "forecast": forecast_items,
            "total_forecasted": total_forecasted,
            "base_value": base_value_total,
            "shap_explanations": [
                {
                    "feature_name": "historical_baseline",
                    "shap_value": 0.0,
                    "description": f"Historical baseline demand is set at {int(historical_baseline)} units/day."
                },
                {
                    "feature_name": "weather_impact",
                    "shap_value": round(total_shap_weather, 2),
                    "description": f"Forecasted local weather/precipitation changes overall demand by {round(total_shap_weather, 1)} units."
                },
                {
                    "feature_name": "seasonality_factors",
                    "shap_value": round(total_shap_seasonality, 2),
                    "description": f"Outbreak patterns and regional seasonal factors changes overall demand by {round(total_shap_seasonality, 1)} units."
                }
            ]
        }

prediction_service = PredictionService()
