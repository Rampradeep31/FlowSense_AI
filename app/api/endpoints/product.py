from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter()

@router.get("", response_model=List[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    """
    List all products in the system.
    """
    result = await db.execute(select(Product))
    return result.scalars().all()

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new product with custom temperature and delay thresholds.
    """
    # Check if product name is already taken
    stmt = select(Product).where(Product.name == payload.name)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with name '{payload.name}' already exists."
        )

    db_product = Product(
        name=payload.name,
        temp_min_c=payload.temp_min_c,
        temp_max_c=payload.temp_max_c,
        max_excursion_duration_minutes=payload.max_excursion_duration_minutes,
        max_delay_hours=payload.max_delay_hours
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    
    return db_product
