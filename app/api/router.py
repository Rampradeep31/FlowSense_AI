from fastapi import APIRouter
from app.api.endpoints import route, weather, news, sensor

api_router = APIRouter()

api_router.include_router(route.router, prefix="/route", tags=["Route Analysis"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather Forecast"])
api_router.include_router(news.router, prefix="/news", tags=["News Disruptions"])
api_router.include_router(sensor.router, prefix="/sensors", tags=["Sensor Simulation"])
