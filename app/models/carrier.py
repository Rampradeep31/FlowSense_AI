from sqlalchemy import Column, Float, Integer, String
from app.database import Base

class Carrier(Base):
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    reliability_pct = Column(Float, default=95.0, nullable=False)
