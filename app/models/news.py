import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from app.database import Base

class NewsDisruption(Base):
    __tablename__ = "news_disruptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(String(20), default="medium", nullable=False)  # low, medium, high
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
