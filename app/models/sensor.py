import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String
from app.database import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    cold_box_id = Column(String(100), index=True, nullable=False)
    shipment_id = Column(String(100), index=True, nullable=True)
    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)
