import logging
import csv
import io
import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.shipment import Shipment
from app.models.product import Product
from app.models.carrier import Carrier
from app.models.sensor import SensorReading
from app.schemas.compliance import (
    ExcursionDetail,
    ShipmentComplianceReport,
    CarrierComplianceRanking,
    MonthlyComplianceSummary
)

logger = logging.getLogger(__name__)

class ComplianceService:
    async def generate_shipment_report(self, db: AsyncSession, shipment_id: int) -> ShipmentComplianceReport:
        """
        Analyzes a shipment's temperature logs to compute contiguous excursion periods,
        overall compliance status, and estimated financial loss.
        """
        stmt = (
            select(Shipment)
            .options(
                selectinload(Shipment.product),
                selectinload(Shipment.carrier),
                selectinload(Shipment.cold_box)
            )
            .where(Shipment.id == shipment_id)
        )
        result = await db.execute(stmt)
        shipment = result.scalars().first()
        if not shipment:
            raise ValueError(f"Shipment with ID {shipment_id} not found.")

        # Fetch telemetry readings in chronological order
        r_stmt = select(SensorReading).where(SensorReading.shipment_id == shipment_id).order_by(SensorReading.timestamp.asc())
        r_res = await db.execute(r_stmt)
        readings = r_res.scalars().all()

        temp_min = shipment.product.temp_min_c if shipment.product else 2.0
        temp_max = shipment.product.temp_max_c if shipment.product else 8.0
        max_duration = shipment.product.max_excursion_duration_minutes if shipment.product else 30.0

        excursions: List[ExcursionDetail] = []
        
        # Trace contiguous excursion periods
        in_excursion = False
        excursion_start = None
        seg_max = -99.0
        seg_min = 99.0

        for r in readings:
            temp = r.temperature_c
            is_breach = temp < temp_min or temp > temp_max

            if is_breach:
                if not in_excursion:
                    in_excursion = True
                    excursion_start = r.timestamp
                    seg_max = temp
                    seg_min = temp
                else:
                    seg_max = max(seg_max, temp)
                    seg_min = min(seg_min, temp)
            else:
                if in_excursion:
                    in_excursion = False
                    duration = (r.timestamp - excursion_start).total_seconds() / 60.0
                    excursions.append(ExcursionDetail(
                        start_time=excursion_start,
                        end_time=r.timestamp,
                        duration_minutes=round(duration, 1),
                        max_temperature=round(seg_max, 2),
                        min_temperature=round(seg_min, 2)
                    ))

        # Handle ongoing excursion at the end of the telemetry log
        if in_excursion and readings:
            last_timestamp = readings[-1].timestamp
            duration = (last_timestamp - excursion_start).total_seconds() / 60.0
            excursions.append(ExcursionDetail(
                start_time=excursion_start,
                end_time=last_timestamp,
                duration_minutes=round(duration, 1),
                max_temperature=round(seg_max, 2),
                min_temperature=round(seg_min, 2)
            ))

        # Tally metrics
        total_transit_hours = 0.0
        if readings:
            total_transit_hours = (readings[-1].timestamp - shipment.departure_time).total_seconds() / 3600.0

        # Determine compliance status: if status is spoiled or any excursion segment exceeds allowed limit
        any_limit_breached = any(e.duration_minutes > max_duration for e in excursions)
        compliance_status = "compliant"
        if shipment.status == "spoiled" or any_limit_breached:
            compliance_status = "non_compliant"

        # Calculate estimated financial loss: assume Rs 250 per vaccine vial
        estimated_loss = 0.0
        if shipment.status == "spoiled" or compliance_status == "non_compliant":
            estimated_loss = shipment.quantity * 250.0

        return ShipmentComplianceReport(
            shipment_id=shipment.id,
            product_name=shipment.product.name if shipment.product else "Unknown",
            carrier_name=shipment.carrier.name if shipment.carrier else "Unknown",
            cold_box_id=shipment.cold_box_id or "Unknown",
            total_transit_hours=round(total_transit_hours, 1),
            status=shipment.status,
            excursions_count=len(excursions),
            excursions=excursions,
            compliance_status=compliance_status,
            estimated_loss_inr=estimated_loss
        )

    async def generate_monthly_summary(self, db: AsyncSession) -> MonthlyComplianceSummary:
        """
        Compiles aggregate compliance metrics across all shipments.
        """
        # Fetch shipments and pre-load carriers
        s_stmt = select(Shipment).options(selectinload(Shipment.carrier))
        s_res = await db.execute(s_stmt)
        shipments = s_res.scalars().all()

        total_shipments = len(shipments)
        safe_deliveries = sum(1 for s in shipments if s.status == "delivered")
        delayed_deliveries = sum(1 for s in shipments if s.status == "delayed")
        spoiled_deliveries = sum(1 for s in shipments if s.status == "spoiled")

        # Total financial loss (Rs 250/vial spoiled)
        total_loss = sum(s.quantity * 250.0 for s in shipments if s.status == "spoiled")

        # Compile carrier compliance scores
        c_stmt = select(Carrier)
        c_res = await db.execute(c_stmt)
        carriers = c_res.scalars().all()

        carrier_rankings: List[CarrierComplianceRanking] = []
        for c in carriers:
            carrier_shipments = [s for s in shipments if s.carrier_id == c.id]
            total_c_shipments = len(carrier_shipments)
            spoiled_c = sum(1 for s in carrier_shipments if s.status == "spoiled")
            delayed_c = sum(1 for s in carrier_shipments if s.status == "delayed")
            delivered_c = sum(1 for s in carrier_shipments if s.status == "delivered")

            # Compliance score = percent of shipments delivered safely (not spoiled)
            safe_c = total_c_shipments - spoiled_c
            score = (safe_c / total_c_shipments * 100.0) if total_c_shipments > 0 else 100.0

            carrier_rankings.append(CarrierComplianceRanking(
                carrier_id=c.id,
                carrier_name=c.name,
                reliability_pct=c.reliability_pct,
                total_shipments=total_c_shipments,
                spoiled_shipments=spoiled_c,
                delayed_shipments=delayed_c,
                compliance_score=round(score, 1)
            ))

        # Sort rankings with highest score first
        carrier_rankings.sort(key=lambda x: x.compliance_score, reverse=True)

        return MonthlyComplianceSummary(
            total_shipments_dispatched=total_shipments,
            safe_deliveries=safe_deliveries,
            delayed_deliveries=delayed_deliveries,
            spoiled_deliveries=spoiled_deliveries,
            total_financial_loss_inr=total_loss,
            carrier_rankings=carrier_rankings
        )

    async def export_shipment_csv(self, db: AsyncSession, shipment_id: int) -> str:
        """
        Exports a shipment's telemetry readings to a CSV formatted string.
        """
        stmt = select(Shipment).options(selectinload(Shipment.product)).where(Shipment.id == shipment_id)
        res = await db.execute(stmt)
        shipment = res.scalars().first()
        if not shipment:
            raise ValueError(f"Shipment with ID {shipment_id} not found.")

        # Fetch telemetry
        r_stmt = select(SensorReading).where(SensorReading.shipment_id == shipment_id).order_by(SensorReading.timestamp.asc())
        r_res = await db.execute(r_stmt)
        readings = r_res.scalars().all()

        temp_min = shipment.product.temp_min_c if shipment.product else 2.0
        temp_max = shipment.product.temp_max_c if shipment.product else 8.0

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Timestamp', 'Temperature_C', 'Humidity_Pct', 'Excursion_Active', 'Safe_Min_C', 'Safe_Max_C'])

        for r in readings:
            is_breach = r.temperature_c < temp_min or r.temperature_c > temp_max
            writer.writerow([
                r.timestamp.isoformat(),
                round(r.temperature_c, 2),
                round(r.humidity_pct, 2),
                'TRUE' if is_breach else 'FALSE',
                temp_min,
                temp_max
            ])

        return output.getvalue()

    async def export_summary_csv(self, db: AsyncSession) -> str:
        """
        Exports aggregate audit records for all shipments to a CSV formatted string.
        """
        s_stmt = select(Shipment).options(
            selectinload(Shipment.product),
            selectinload(Shipment.carrier)
        ).order_by(Shipment.id.asc())
        s_res = await db.execute(s_stmt)
        shipments = s_res.scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Shipment ID', 'Origin', 'Destination', 'Product Name', 
            'Carrier Name', 'Quantity Vials', 'Status', 'Estimated Loss INR', 'Departure Time'
        ])

        for s in shipments:
            loss = s.quantity * 250.0 if s.status == "spoiled" else 0.0
            writer.writerow([
                s.id,
                s.origin,
                s.destination,
                s.product.name if s.product else 'Unknown',
                s.carrier.name if s.carrier else 'Unknown',
                s.quantity,
                s.status,
                loss,
                s.departure_time.isoformat()
            ])

        return output.getvalue()

compliance_service = ComplianceService()
