import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    temp_min_c = Column(Float, default=2.0, nullable=False)
    temp_max_c = Column(Float, default=8.0, nullable=False)
    max_excursion_duration_minutes = Column(Integer, default=30, nullable=False)
    max_delay_hours = Column(Float, default=24.0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
