from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.simulation import WhatIfRequest, WhatIfResponse, RecommendationResponse
from app.services.simulation import simulation_service

router = APIRouter()

@router.post("/what-if", response_model=WhatIfResponse)
async def run_what_if_simulation(payload: WhatIfRequest, db: AsyncSession = Depends(get_db)):
    """
    Simulate hypothetical shipment parameter overrides (carrier, cold box, departure time)
    and compare predicted delay/spoilage risks to original settings.
    """
    try:
        result = await simulation_service.run_what_if(db, payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"What-If simulation failed: {str(e)}"
        )

@router.get("/recommendations/{shipment_id}", response_model=RecommendationResponse)
async def get_optimization_recommendations(shipment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve automated ranked suggestions (switches, upgrades, schedule delays)
    to reduce predicted delay and spoilage probability.
    """
    try:
        result = await simulation_service.get_recommendations(db, shipment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate decision recommendations: {str(e)}"
        )
