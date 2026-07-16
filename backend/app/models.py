from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
import datetime
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    predictions = relationship("PredictionHistory", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False, index=True)
    product_cost = Column(Float, nullable=False)
    delivery_time = Column(Integer, nullable=False)       # in days
    quality_rating = Column(Float, nullable=False)        # 1.0 to 5.0
    late_deliveries = Column(Integer, nullable=False)      # count of late orders
    experience = Column(Integer, nullable=False)           # years
    contact_info = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    recommendations = relationship("Recommendation", back_populates="supplier")


class FreightHistory(Base):
    __tablename__ = "freight_history"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    distance = Column(Float, nullable=False)
    fuel_price = Column(Float, nullable=False)
    month = Column(String(20), nullable=False)
    freight_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    distance = Column(Float, nullable=False)
    fuel_price = Column(Float, nullable=False)
    month = Column(String(20), nullable=False)
    predicted_freight_cost = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)       # e.g., percentage like 92.5
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="predictions")
    recommendations = relationship("Recommendation", back_populates="prediction")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    prediction_id = Column(Integer, ForeignKey("prediction_history.id", ondelete="CASCADE"), nullable=False)
    recommended_supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    total_landed_cost = Column(Float, nullable=False)
    product_cost = Column(Float, nullable=False)
    predicted_freight_cost = Column(Float, nullable=False)
    risk_premium = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="recommendations")
    prediction = relationship("PredictionHistory", back_populates="recommendations")
    supplier = relationship("Supplier", back_populates="recommendations")
