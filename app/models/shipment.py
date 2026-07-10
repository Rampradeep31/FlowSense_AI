import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    cold_box_id = Column(String(100), ForeignKey("cold_boxes.id", ondelete="RESTRICT"), nullable=False)
    carrier_id = Column(Integer, ForeignKey("carriers.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(30), default="created", nullable=False)  # created, in-transit, delayed, delivered, spoiled
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="SET NULL"), nullable=True)
    departure_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    product = relationship("Product")
    cold_box = relationship("ColdBox")
    carrier = relationship("Carrier")
    route = relationship("Route")
