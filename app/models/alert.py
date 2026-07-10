import datetime
from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from app.database import Base
from sqlalchemy.orm import relationship

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # temp_breach, delay_breach
    severity = Column(String(20), default="medium", nullable=False)  # info, warning, critical
    message = Column(Text, nullable=False)
    why_info = Column(JSON, nullable=False)  # {"what": "", "why": "", "suggested_action": ""}
    is_acknowledged = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    shipment = relationship("Shipment")
