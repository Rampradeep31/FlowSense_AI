import datetime
from sqlalchemy import JSON, Column, DateTime, Float, Integer, Text
from app.database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    waypoints = Column(JSON, nullable=False)  # [[lon, lat], [lon, lat], ...]
    distance_km = Column(Float, nullable=False)
    duration_hours = Column(Float, nullable=False)
    geometry = Column(Text, nullable=False)  # Polyline string
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
