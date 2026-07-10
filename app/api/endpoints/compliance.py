from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.compliance import ShipmentComplianceReport, MonthlyComplianceSummary
from app.services.compliance import compliance_service

router = APIRouter()

@router.get("/shipment/{shipment_id}/report", response_model=ShipmentComplianceReport)
async def get_shipment_compliance_report(shipment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieves detailed temperature excursion timelines, transit durations,
    and compliance audits for a specific shipment.
    """
    try:
        result = await compliance_service.generate_shipment_report(db, shipment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate shipment compliance report: {str(e)}"
        )

@router.get("/shipment/{shipment_id}/export")
async def export_shipment_telemetry_csv(shipment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Downloads raw temperature readings, humidity, and breach indicators for a shipment as a CSV file.
    """
    try:
        csv_data = await compliance_service.export_shipment_csv(db, shipment_id)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=shipment_{shipment_id}_excursion_log.csv"}
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export shipment telemetry to CSV: {str(e)}"
        )

@router.get("/summary", response_model=MonthlyComplianceSummary)
async def get_monthly_compliance_summary(db: AsyncSession = Depends(get_db)):
    """
    Retrieves district-wide monthly compliance summary (shipments dispatch totals,
    spoiled/delayed counts, cumulative loss tracking, and carrier reliability rankings).
    """
    try:
        result = await compliance_service.generate_monthly_summary(db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile compliance summary: {str(e)}"
        )

@router.get("/summary/export")
async def export_monthly_summary_csv(db: AsyncSession = Depends(get_db)):
    """
    Downloads general monthly audit records for all shipments as a CSV file.
    """
    try:
        csv_data = await compliance_service.export_summary_csv(db)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=district_monthly_audit_summary.csv"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export monthly summary CSV: {str(e)}"
        )
