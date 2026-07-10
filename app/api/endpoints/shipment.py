import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
from app.database import get_db
from app.models.shipment import Shipment
from app.models.product import Product
from app.models.cold_box import ColdBox
from app.models.carrier import Carrier
from app.models.route import Route
from app.models.sensor import SensorReading
from app.schemas.shipment import ShipmentCreate, ShipmentResponse, ShipmentDetailResponse
from app.schemas.sensor import SensorReadingSchema
from app.services.route import route_service
from app.services.weather import weather_service
from app.services.news import news_service

logger = logging.getLogger(__name__)
router = APIRouter()

CITY_COORDINATES = {
    "mumbai": [72.8777, 19.0760],
    "pune": [73.8567, 18.5204],
    "nashik": [73.7898, 19.9975],
    "nagpur": [79.0882, 21.1458],
    "aurangabad": [75.3433, 19.8762],
    "thane": [72.9525, 19.2183],
    "kolhapur": [74.2433, 16.7050],
    "solapur": [75.9064, 17.6599],
    "jalgaon": [75.5626, 21.0074],
    "amravati": [77.7523, 20.9374],
    "nanded": [77.3079, 19.1383],
    "sangli": [74.5636, 16.8524],
    "satara": [73.9850, 17.6805],
    "latur": [76.5647, 18.4088],
    "dhule": [74.7749, 20.8997],
}

def geocode_city(city_name: str) -> List[float]:
    normalized = city_name.strip().lower()
    if normalized in CITY_COORDINATES:
        return CITY_COORDINATES[normalized]
    logger.info(f"City '{city_name}' not in registry. Defaulting to Mumbai coordinates.")
    return CITY_COORDINATES["mumbai"]

@router.post("", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_shipment(payload: ShipmentCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new shipment. Automatically triggers route analysis to link a route,
    and initializes status to 'in-transit'.
    """
    # Verify relations exist
    product = (await db.execute(select(Product).where(Product.id == payload.product_id))).scalars().first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with ID {payload.product_id} not found.")

    cold_box = (await db.execute(select(ColdBox).where(ColdBox.id == payload.cold_box_id))).scalars().first()
    if not cold_box:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cold Box with ID '{payload.cold_box_id}' not found.")

    carrier = (await db.execute(select(Carrier).where(Carrier.id == payload.carrier_id))).scalars().first()
    if not carrier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Carrier with ID {payload.carrier_id} not found.")

    # Geocode standard Maharashtra route endpoints
    origin_coords = geocode_city(payload.origin)
    dest_coords = geocode_city(payload.destination)
    
    # Automatically trigger route analysis
    try:
        analysis = await route_service.analyze_route([origin_coords, dest_coords])
        
        db_route = Route(
            waypoints=analysis["waypoints"],
            distance_km=analysis["distance_km"],
            duration_hours=analysis["duration_hours"],
            geometry=analysis["geometry"]
        )
        db.add(db_route)
        await db.commit()
        await db.refresh(db_route)
        route_id = db_route.id
    except Exception as e:
        logger.error(f"Automated route analysis failed during shipment creation: {e}")
        route_id = None

    db_shipment = Shipment(
        origin=payload.origin,
        destination=payload.destination,
        product_id=payload.product_id,
        quantity=payload.quantity,
        cold_box_id=payload.cold_box_id,
        carrier_id=payload.carrier_id,
        departure_time=payload.departure_time,
        route_id=route_id,
        status="in-transit"
    )
    db.add(db_shipment)
    await db.commit()
    await db.refresh(db_shipment)
    
    return db_shipment

@router.get("", response_model=List[ShipmentDetailResponse])
async def list_shipments(db: AsyncSession = Depends(get_db)):
    """
    List all shipments with fully resolved product, carrier, cold box, and route relationships.
    """
    result = await db.execute(
        select(Shipment).options(
            selectinload(Shipment.product),
            selectinload(Shipment.cold_box),
            selectinload(Shipment.carrier),
            selectinload(Shipment.route)
        )
    )
    return result.scalars().all()

@router.get("/{id}/status")
async def get_shipment_status(id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetch current status of a shipment, combined with linked real-time weather forecasts
    and news disruptions along the route waypoints.
    """
    result = await db.execute(
        select(Shipment)
        .options(
            selectinload(Shipment.product),
            selectinload(Shipment.cold_box),
            selectinload(Shipment.carrier),
            selectinload(Shipment.route)
        )
        .where(Shipment.id == id)
    )
    shipment = result.scalars().first()
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Shipment with ID {id} not found.")

    weather_data = []
    news_data = []

    # Fetch weather and news if route exists
    if shipment.route:
        waypoints = shipment.route.waypoints
        try:
            weather_data = await weather_service.get_forecast(waypoints)
        except Exception as e:
            logger.error(f"Failed to fetch linked weather: {e}")

        try:
            news_data = await news_service.get_disruptions(waypoints)
        except Exception as e:
            logger.error(f"Failed to fetch linked news disruptions: {e}")

    return {
        "shipment": ShipmentDetailResponse.model_validate(shipment),
        "weather": weather_data,
        "news_disruptions": news_data
    }

@router.get("/{id}/temperature-log", response_model=List[SensorReadingSchema])
async def get_temperature_log(id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve historical cold box sensor readings recorded since this shipment departed.
    """
    shipment = (await db.execute(select(Shipment).where(Shipment.id == id))).scalars().first()
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Shipment with ID {id} not found.")

    stmt = select(SensorReading).where(
        SensorReading.cold_box_id == shipment.cold_box_id,
        SensorReading.timestamp >= shipment.departure_time
    ).order_by(SensorReading.timestamp.asc())
    
    result = await db.execute(stmt)
    return result.scalars().all()
