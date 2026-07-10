from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.sensor import SensorSimulateRequest, SensorSimulateResponse
from app.services.sensor import sensor_simulator

router = APIRouter()

@router.post("/simulate", response_model=SensorSimulateResponse, status_code=status.HTTP_201_CREATED)
async def simulate_sensor_readings(payload: SensorSimulateRequest, db: AsyncSession = Depends(get_db)):
    """
    Generate simulated temperature and humidity sensor readings for a cold box.
    Healthy box fluctuates in 2-8°C. Failing box climbs to ~15°C.
    Readings are saved to the database.
    """
    try:
        readings = await sensor_simulator.generate_readings(
            db=db,
            cold_box_id=payload.cold_box_id,
            shipment_id=payload.shipment_id,
            failing=payload.failing,
            duration_minutes=payload.duration_minutes,
            interval_minutes=payload.interval_minutes
        )
        return {"readings": readings}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to simulate readings: {e}")
