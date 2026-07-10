from sqlalchemy import Column, Integer, String
from app.database import Base

class ColdBox(Base):
    __tablename__ = "cold_boxes"

    id = Column(String(100), primary_key=True, index=True)
    model = Column(String(100), nullable=False)
    age_months = Column(Integer, nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, inactive
