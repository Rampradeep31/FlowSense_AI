from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.weather import WeatherRequest, WeatherForecastResponse
from app.models.route import Route
from app.models.weather import WeatherForecast
from app.services.weather import weather_service
import datetime

router = APIRouter()

@router.post("/forecast", response_model=WeatherForecastResponse, status_code=status.HTTP_200_OK)
async def get_weather_forecast(payload: WeatherRequest, db: AsyncSession = Depends(get_db)):
    """
    Retrieve 5-day weather forecasts at route waypoints.
    Accepts either direct waypoints or a database route_id.
    Saves the forecast history to the database.
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
        forecast_data = await weather_service.get_forecast(waypoints)

        db_forecasts = []
        for wp_forecast in forecast_data:
            wp_idx = wp_forecast["waypoint_index"]
            lat = wp_forecast["latitude"]
            lon = wp_forecast["longitude"]
            
            for item in wp_forecast["forecast"]:
                t = item["time"]
                if isinstance(t, str):
                    # Strip 'Z' if present, to parse properly
                    if t.endswith("Z"):
                        t = t[:-1]
                    t = datetime.datetime.fromisoformat(t)
                    
                db_forecast = WeatherForecast(
                    route_id=route_id,
                    waypoint_index=wp_idx,
                    latitude=lat,
                    longitude=lon,
                    temp_c=item["temp_c"],
                    humidity_pct=item["humidity_pct"],
                    precipitation_mm=item["precipitation_mm"],
                    forecast_time=t
                )
                db_forecasts.append(db_forecast)

        db.add_all(db_forecasts)
        await db.commit()

        return {"forecasts": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch weather: {e}")
