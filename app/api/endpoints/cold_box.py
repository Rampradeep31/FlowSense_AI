from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.cold_box import ColdBox
from app.schemas.cold_box import ColdBoxCreate, ColdBoxResponse

router = APIRouter()

@router.get("", response_model=List[ColdBoxResponse])
async def list_cold_boxes(db: AsyncSession = Depends(get_db)):
    """
    List all cold boxes available in the system.
    """
    result = await db.execute(select(ColdBox))
    return result.scalars().all()

@router.post("", response_model=ColdBoxResponse, status_code=status.HTTP_201_CREATED)
async def create_cold_box(payload: ColdBoxCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new cold box device with age and status details.
    """
    stmt = select(ColdBox).where(ColdBox.id == payload.id)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cold box with ID '{payload.id}' already exists."
        )

    db_cold_box = ColdBox(
        id=payload.id,
        model=payload.model,
        age_months=payload.age_months,
        status=payload.status
    )
    db.add(db_cold_box)
    await db.commit()
    await db.refresh(db_cold_box)
    
    return db_cold_box
