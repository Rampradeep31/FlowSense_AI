import logging
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.shipment import Shipment
from app.models.alert import Alert
from app.models.sensor import SensorReading
from app.services.websocket import manager
import json

logger = logging.getLogger(__name__)

class AlertRulesEngine:
    async def check_shipment_alerts(self, db: AsyncSession, shipment_id: int) -> None:
        """
        Executes cold chain violation checks for a specific shipment.
        Checks:
        1. Delay Breach: Transit duration exceeds product safe window.
        2. Temperature Excursion: Temp out of bounds (e.g. >8°C) for >30 minutes continuously.
        """
        # Load shipment with product info
        result = await db.execute(
            select(Shipment)
            .options(selectinload(Shipment.product))
            .where(Shipment.id == shipment_id)
        )
        shipment = result.scalars().first()
        if not shipment:
            logger.warning(f"Rules engine: Shipment ID {shipment_id} not found.")
            return

        # Fetch linked product
        product = shipment.product
        if not product:
            logger.warning(f"Rules engine: Shipment ID {shipment_id} has no product definition.")
            return

        now = datetime.datetime.utcnow()

        # ----------------------------------------------------
        # 1. DELAY BREACH CHECK
        # ----------------------------------------------------
        if shipment.status in ["created", "in-transit", "delayed"]:
            transit_duration_hours = (now - shipment.departure_time).total_seconds() / 3600.0
            
            if transit_duration_hours > product.max_delay_hours:
                # Check if a delay alert already exists
                exists_query = select(Alert).where(
                    Alert.shipment_id == shipment.id,
                    Alert.alert_type == "delay_breach"
                )
                alert_exists = (await db.execute(exists_query)).scalars().first()
                
                if not alert_exists:
                    why_data = {
                        "what": f"Safe transit delay limit exceeded for {product.name}",
                        "why": f"Shipment has been in transit for {round(transit_duration_hours, 1)} hours, exceeding the safe threshold of {product.max_delay_hours} hours.",
                        "suggested_action": f"Contact the logistics carrier immediately or activate district buffer stocks at the destination."
                    }
                    alert = Alert(
                        shipment_id=shipment.id,
                        alert_type="delay_breach",
                        severity="warning" if shipment.status == "created" else "critical",
                        message=f"Shipment transit duration of {round(transit_duration_hours, 1)}h exceeds limit of {product.max_delay_hours}h.",
                        why_info=why_data
                    )
                    db.add(alert)
                    
                    # Update status
                    shipment.status = "delayed"
                    db.add(shipment)
                    await db.commit()
                    await db.refresh(alert)
                    
                    # Broadcast alert
                    await manager.broadcast_alert({
                        "id": alert.id,
                        "shipment_id": alert.shipment_id,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "why_info": alert.why_info,
                        "created_at": alert.created_at
                    })
                    logger.info(f"Rules engine: Raised delay breach alert for Shipment {shipment.id}.")

        # ----------------------------------------------------
        # 2. TEMPERATURE BREACH CHECK
        # ----------------------------------------------------
        # Fetch cold box readings chronologically since the shipment departure time
        readings_query = select(SensorReading).where(
            SensorReading.cold_box_id == shipment.cold_box_id,
            SensorReading.timestamp >= shipment.departure_time
        ).order_by(SensorReading.timestamp.asc())
        
        readings_result = await db.execute(readings_query)
        readings = readings_result.scalars().all()

        excursion_start = None
        excursion_detected = False
        excursion_duration = 0.0

        for r in readings:
            temp_out_of_bounds = (r.temperature_c > product.temp_max_c) or (r.temperature_c < product.temp_min_c)
            
            if temp_out_of_bounds:
                if excursion_start is None:
                    excursion_start = r.timestamp
                
                duration_mins = (r.timestamp - excursion_start).total_seconds() / 60.0
                if duration_mins > product.max_excursion_duration_minutes:
                    excursion_detected = True
                    excursion_duration = duration_mins
            else:
                # Reset excursion window if temperature goes back to normal bounds
                excursion_start = None

        if excursion_detected:
            # Check if a temperature alert already exists
            exists_query = select(Alert).where(
                Alert.shipment_id == shipment.id,
                Alert.alert_type == "temp_breach"
            )
            alert_exists = (await db.execute(exists_query)).scalars().first()
            
            if not alert_exists:
                why_data = {
                    "what": f"Continuous temperature excursion for {product.name}",
                    "why": f"Sensor readings report cold box temperature was out of the safe {product.temp_min_c}°C-{product.temp_max_c}°C range for {round(excursion_duration, 1)} minutes continuously, exceeding the product limit of {product.max_excursion_duration_minutes} minutes.",
                    "suggested_action": "Direct the District Cold Chain Officer to verify packaging insulation, check box seals, or transfer products to standard refrigerator immediately."
                }
                
                alert = Alert(
                    shipment_id=shipment.id,
                    alert_type="temp_breach",
                    severity="critical",
                    message=f"Cold box temperature breached safe limits ({product.temp_min_c}-{product.temp_max_c}°C) for >{product.max_excursion_duration_minutes} mins.",
                    why_info=why_data
                )
                db.add(alert)
                
                # Mark shipment as spoiled due to cold chain breach
                shipment.status = "spoiled"
                db.add(shipment)
                await db.commit()
                await db.refresh(alert)
                
                # Broadcast alert
                await manager.broadcast_alert({
                    "id": alert.id,
                    "shipment_id": alert.shipment_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "why_info": alert.why_info,
                    "created_at": alert.created_at
                })
                logger.info(f"Rules engine: Raised critical temperature excursion alert for Shipment {shipment.id}.")

rules_engine = AlertRulesEngine()
