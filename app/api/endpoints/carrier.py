from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.carrier import Carrier
from app.schemas.carrier import CarrierCreate, CarrierResponse

router = APIRouter()

@router.get("", response_model=List[CarrierResponse])
async def list_carriers(db: AsyncSession = Depends(get_db)):
    """
    List all registered carriers in the system.
    """
    result = await db.execute(select(Carrier))
    return result.scalars().all()

@router.post("", response_model=CarrierResponse, status_code=status.HTTP_201_CREATED)
async def create_carrier(payload: CarrierCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new logistics carrier and set their reliability index.
    """
    stmt = select(Carrier).where(Carrier.name == payload.name)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Carrier with name '{payload.name}' already exists."
        )

    db_carrier = Carrier(
        name=payload.name,
        reliability_pct=payload.reliability_pct
    )
    db.add(db_carrier)
    await db.commit()
    await db.refresh(db_carrier)
    
    return db_carrier
