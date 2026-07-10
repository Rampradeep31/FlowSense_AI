from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.database import get_db
from app.schemas.prediction import (
    DelayPredictionRequest,
    DelayPredictionResponse,
    SpoilagePredictionRequest,
    SpoilagePredictionResponse,
    DemandPredictionRequest,
    DemandPredictionResponse,
)
from app.services.prediction import prediction_service
from app.models.demand import DemandForecast

router = APIRouter()

@router.post("/delay", response_model=DelayPredictionResponse)
async def predict_shipment_delay(payload: DelayPredictionRequest, db: AsyncSession = Depends(get_db)):
    """
    Predict expected transit delay in hours and probability of delay, along with exact SHAP explanations.
    """
    try:
        pred = await prediction_service.predict_delay(db, payload.shipment_id)
        return pred
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delay prediction failed: {str(e)}"
        )

@router.post("/spoilage", response_model=SpoilagePredictionResponse)
async def predict_shipment_spoilage(payload: SpoilagePredictionRequest, db: AsyncSession = Depends(get_db)):
    """
    Predict probability of product spoilage and risk categories (low, medium, high), explained with SHAP.
    """
    try:
        pred = await prediction_service.predict_spoilage(db, payload.shipment_id)
        return pred
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Spoilage prediction failed: {str(e)}"
        )

@router.post("/demand", response_model=DemandPredictionResponse)
async def predict_destination_demand(payload: DemandPredictionRequest, db: AsyncSession = Depends(get_db)):
    """
    Forecast clinic vaccine/medicine demand for the next 7 days, explained with SHAP.
    Saves generated forecasts to the database for auditing.
    """
    try:
        pred = await prediction_service.forecast_demand(
            db=db,
            product_id=payload.product_id,
            destination=payload.destination,
            forecast_days=payload.forecast_days
        )

        # Persist daily forecasts to the database
        for item in pred["forecast"]:
            db_forecast = DemandForecast(
                product_id=payload.product_id,
                destination=payload.destination,
                forecast_date=item["date"],
                forecasted_quantity=item["quantity"]
            )
            db.add(db_forecast)
        
        await db.commit()
        return pred
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demand forecasting failed: {str(e)}"
        )
