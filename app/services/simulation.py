import logging
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.shipment import Shipment
from app.models.product import Product
from app.models.cold_box import ColdBox
from app.models.carrier import Carrier
from app.schemas.simulation import WhatIfRequest
from app.services.prediction import prediction_service

logger = logging.getLogger(__name__)

class SimulationService:
    async def run_what_if(self, db: AsyncSession, payload: WhatIfRequest) -> Dict[str, Any]:
        """
        Runs in-memory simulation by copying a shipment and overriding parameters.
        Compares results with original shipment predictions.
        """
        # 1. Fetch original shipment
        stmt = (
            select(Shipment)
            .options(
                selectinload(Shipment.product),
                selectinload(Shipment.carrier),
                selectinload(Shipment.cold_box),
                selectinload(Shipment.route)
            )
            .where(Shipment.id == payload.shipment_id)
        )
        result = await db.execute(stmt)
        shipment = result.scalars().first()
        if not shipment:
            raise ValueError(f"Shipment with ID {payload.shipment_id} not found.")

        # 2. Compute original predictions
        orig_delay = await prediction_service.predict_delay_for_shipment(db, shipment)
        orig_spoilage = await prediction_service.predict_spoilage_for_shipment(
            db, shipment, orig_delay["predicted_delay_hours"]
        )

        # 3. Create simulated copy in memory
        sim_shipment = Shipment(
            id=shipment.id,
            origin=shipment.origin,
            destination=shipment.destination,
            product_id=shipment.product_id,
            quantity=shipment.quantity,
            cold_box_id=shipment.cold_box_id,
            carrier_id=shipment.carrier_id,
            departure_time=shipment.departure_time,
            route_id=shipment.route_id,
            status=shipment.status
        )
        # Bind preloaded product & route
        sim_shipment.product = shipment.product
        sim_shipment.route = shipment.route
        sim_shipment.carrier = shipment.carrier
        sim_shipment.cold_box = shipment.cold_box

        # Apply overrides
        if payload.carrier_id is not None:
            c_stmt = select(Carrier).where(Carrier.id == payload.carrier_id)
            c_res = await db.execute(c_stmt)
            carrier = c_res.scalars().first()
            if carrier:
                sim_shipment.carrier = carrier
                sim_shipment.carrier_id = carrier.id

        if payload.cold_box_id is not None:
            b_stmt = select(ColdBox).where(ColdBox.id == payload.cold_box_id)
            b_res = await db.execute(b_stmt)
            cold_box = b_res.scalars().first()
            if cold_box:
                sim_shipment.cold_box = cold_box
                sim_shipment.cold_box_id = cold_box.id

        if payload.departure_time is not None:
            sim_shipment.departure_time = payload.departure_time

        # 4. Compute simulated predictions
        sim_delay = await prediction_service.predict_delay_for_shipment(db, sim_shipment)
        sim_spoilage = await prediction_service.predict_spoilage_for_shipment(
            db, sim_shipment, sim_delay["predicted_delay_hours"]
        )

        # 5. Compute reductions
        delay_reduction = orig_delay["predicted_delay_hours"] - sim_delay["predicted_delay_hours"]
        spoilage_reduction_pct = (orig_spoilage["spoilage_probability"] - sim_spoilage["spoilage_probability"]) * 100.0

        return {
            "shipment_id": shipment.id,
            "original_delay_hours": orig_delay["predicted_delay_hours"],
            "original_spoilage_probability": orig_spoilage["spoilage_probability"],
            "original_risk_category": orig_spoilage["risk_category"],
            "simulated_delay_hours": sim_delay["predicted_delay_hours"],
            "simulated_spoilage_probability": sim_spoilage["spoilage_probability"],
            "simulated_risk_category": sim_spoilage["risk_category"],
            "delay_reduction_hours": round(delay_reduction, 2),
            "spoilage_reduction_pct": round(spoilage_reduction_pct, 2),
            "shap_explanations": sim_spoilage["shap_explanations"]
        }

    async def get_recommendations(self, db: AsyncSession, shipment_id: int) -> Dict[str, Any]:
        """
        Runs simulations across alternative carriers, cold boxes, and shifted departure times.
        Returns ranked optimization suggestions.
        """
        # Fetch shipment
        stmt = (
            select(Shipment)
            .options(
                selectinload(Shipment.product),
                selectinload(Shipment.carrier),
                selectinload(Shipment.cold_box),
                selectinload(Shipment.route)
            )
            .where(Shipment.id == shipment_id)
        )
        result = await db.execute(stmt)
        shipment = result.scalars().first()
        if not shipment:
            raise ValueError(f"Shipment with ID {shipment_id} not found.")

        # Compute nominal baselines
        orig_delay = await prediction_service.predict_delay_for_shipment(db, shipment)
        orig_spoilage = await prediction_service.predict_spoilage_for_shipment(
            db, shipment, orig_delay["predicted_delay_hours"]
        )

        orig_delay_hours = orig_delay["predicted_delay_hours"]
        orig_spoilage_prob = orig_spoilage["spoilage_probability"]

        recommendations = []

        # 1. Simulate Alternative Carriers
        carriers_stmt = select(Carrier).where(Carrier.id != shipment.carrier_id)
        carriers_res = await db.execute(carriers_stmt)
        carriers = carriers_res.scalars().all()

        for c in carriers:
            # Create WhatIf simulation payload in-memory
            sim_shipment = self._clone_shipment(shipment)
            sim_shipment.carrier = c
            sim_shipment.carrier_id = c.id

            sim_delay = await prediction_service.predict_delay_for_shipment(db, sim_shipment)
            sim_spoilage = await prediction_service.predict_spoilage_for_shipment(
                db, sim_shipment, sim_delay["predicted_delay_hours"]
            )

            del_red = orig_delay_hours - sim_delay["predicted_delay_hours"]
            spoil_red = (orig_spoilage_prob - sim_spoilage["spoilage_probability"]) * 100.0

            if del_red > 0.05 or spoil_red > 0.05:
                recommendations.append({
                    "type": "carrier_upgrade",
                    "description": f"Switch logistics carrier to '{c.name}' (reliability rate of {c.reliability_pct}%).",
                    "predicted_delay_reduction_hours": round(del_red, 2),
                    "predicted_spoilage_reduction_pct": round(spoil_red, 2),
                    "actionable_details": {"carrier_id": c.id}
                })

        # 2. Simulate Alternative Active Cold Boxes
        boxes_stmt = select(ColdBox).where(ColdBox.id != shipment.cold_box_id, ColdBox.status == "active")
        boxes_res = await db.execute(boxes_stmt)
        boxes = boxes_res.scalars().all()

        for b in boxes:
            sim_shipment = self._clone_shipment(shipment)
            sim_shipment.cold_box = b
            sim_shipment.cold_box_id = b.id

            # Carrier is original
            sim_delay = await prediction_service.predict_delay_for_shipment(db, sim_shipment)
            sim_spoilage = await prediction_service.predict_spoilage_for_shipment(
                db, sim_shipment, sim_delay["predicted_delay_hours"]
            )

            del_red = orig_delay_hours - sim_delay["predicted_delay_hours"]
            spoil_red = (orig_spoilage_prob - sim_spoilage["spoilage_probability"]) * 100.0

            if spoil_red > 0.05:
                recommendations.append({
                    "type": "box_upgrade",
                    "description": f"Upgrade container insulation to newer cold box '{b.id}' (Model: {b.model}, age: {b.age_months} months).",
                    "predicted_delay_reduction_hours": round(del_red, 2),
                    "predicted_spoilage_reduction_pct": round(spoil_red, 2),
                    "actionable_details": {"cold_box_id": b.id}
                })

        # 3. Simulate Shifting Departure Times (+6h and +12h)
        for hours in [6, 12]:
            shifted_time = shipment.departure_time + datetime.timedelta(hours=hours)
            sim_shipment = self._clone_shipment(shipment)
            sim_shipment.departure_time = shifted_time

            sim_delay = await prediction_service.predict_delay_for_shipment(db, sim_shipment)
            sim_spoilage = await prediction_service.predict_spoilage_for_shipment(
                db, sim_shipment, sim_delay["predicted_delay_hours"]
            )

            del_red = orig_delay_hours - sim_delay["predicted_delay_hours"]
            spoil_red = (orig_spoilage_prob - sim_spoilage["spoilage_probability"]) * 100.0

            if del_red > 0.05 or spoil_red > 0.05:
                recommendations.append({
                    "type": "departure_shift",
                    "description": f"Delay shipment departure by {hours} hours to bypass adverse weather risks and route heat peaks.",
                    "predicted_delay_reduction_hours": round(del_red, 2),
                    "predicted_spoilage_reduction_pct": round(spoil_red, 2),
                    "actionable_details": {"departure_time": shifted_time.isoformat()}
                })

        # Sort recommendations by spoilage reduction first, delay reduction second (descending)
        recommendations.sort(
            key=lambda x: (x["predicted_spoilage_reduction_pct"], x["predicted_delay_reduction_hours"]),
            reverse=True
        )

        return {
            "shipment_id": shipment_id,
            "original_risk_category": orig_spoilage["risk_category"],
            "recommendations": recommendations
        }

    def _clone_shipment(self, shipment: Shipment) -> Shipment:
        """
        Creates a shallow clone copy of the shipment and preloaded relations.
        """
        cloned = Shipment(
            id=shipment.id,
            origin=shipment.origin,
            destination=shipment.destination,
            product_id=shipment.product_id,
            quantity=shipment.quantity,
            cold_box_id=shipment.cold_box_id,
            carrier_id=shipment.carrier_id,
            departure_time=shipment.departure_time,
            route_id=shipment.route_id,
            status=shipment.status
        )
        cloned.product = shipment.product
        cloned.route = shipment.route
        cloned.carrier = shipment.carrier
        cloned.cold_box = shipment.cold_box
        return cloned

simulation_service = SimulationService()
