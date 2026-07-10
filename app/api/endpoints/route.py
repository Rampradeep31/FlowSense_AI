from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.route import RouteRequest, RouteResponse
from app.models.route import Route
from app.services.route import route_service

router = APIRouter()

@router.post("/analyze", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
async def analyze_route(payload: RouteRequest, db: AsyncSession = Depends(get_db)):
    """
    Analyze waypoints to return distance, duration, and geometry.
    Saves the analyzed route in the database.
    """
    try:
        analysis = await route_service.analyze_route(payload.waypoints)
        
        db_route = Route(
            waypoints=analysis["waypoints"],
            distance_km=analysis["distance_km"],
            duration_hours=analysis["duration_hours"],
            geometry=analysis["geometry"]
        )
        db.add(db_route)
        await db.commit()
        await db.refresh(db_route)
        
        return db_route
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to analyze route: {e}")
