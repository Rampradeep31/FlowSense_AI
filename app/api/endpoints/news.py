from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.news import NewsRequest, NewsDisruptionResponse
from app.models.route import Route
from app.models.news import NewsDisruption
from app.services.news import news_service
import datetime

router = APIRouter()

@router.post("/disruptions", response_model=NewsDisruptionResponse, status_code=status.HTTP_200_OK)
async def get_disruptions(payload: NewsRequest, db: AsyncSession = Depends(get_db)):
    """
    Retrieve disruption news (strikes, floods, road closures) within the specified radius of the route.
    Saves new disruptions to the database.
    """
    waypoints = payload.waypoints
    route_id = payload.route_id

    if route_id is not None:
        result = await db.execute(select(Route).where(Route.id == route_id))
        route = result.scalars().first()
        if not route:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Route with ID {route_id} not found.")
        waypoints = route.waypoints

    if not waypoints:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either waypoints or a valid route_id must be provided."
        )

    try:
        disruptions = await news_service.get_disruptions(waypoints, payload.radius_km)

        for item in disruptions:
            t = item["published_at"]
            if isinstance(t, str):
                if t.endswith("Z"):
                    t = t[:-1]
                t = datetime.datetime.fromisoformat(t)

            # Check if this disruption is already stored
            exists_query = select(NewsDisruption).where(
                NewsDisruption.title == item["title"],
                NewsDisruption.published_at == t
            )
            exists_result = await db.execute(exists_query)
            if not exists_result.scalars().first():
                db_news = NewsDisruption(
                    title=item["title"],
                    description=item.get("description"),
                    source=item.get("source"),
                    url=item.get("url"),
                    latitude=item["latitude"],
                    longitude=item["longitude"],
                    severity=item.get("severity", "medium"),
                    published_at=t
                )
                db.add(db_news)
        
        await db.commit()

        return {"disruptions": disruptions}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch news: {e}")
