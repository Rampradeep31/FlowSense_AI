from fastapi import APIRouter
from app.api.endpoints import (
    route,
    weather,
    news,
    sensor,
    product,
    cold_box,
    carrier,
    shipment,
    alert,
    prediction,
)

api_router = APIRouter()

api_router.include_router(route.router, prefix="/route", tags=["Route Analysis"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather Forecast"])
api_router.include_router(news.router, prefix="/news", tags=["News Disruptions"])
api_router.include_router(sensor.router, prefix="/sensors", tags=["Sensor Simulation"])
api_router.include_router(product.router, prefix="/products", tags=["Product Management"])
api_router.include_router(cold_box.router, prefix="/cold-boxes", tags=["Cold Box Management"])
api_router.include_router(carrier.router, prefix="/carriers", tags=["Carrier Management"])
api_router.include_router(shipment.router, prefix="/shipments", tags=["Shipment Tracking"])
api_router.include_router(alert.router, prefix="/alerts", tags=["Alert Management"])
api_router.include_router(prediction.router, prefix="/predictions", tags=["AI Predictions"])
