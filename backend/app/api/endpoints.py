from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from backend.app.database import get_db
from backend.app.models import User, Supplier, PredictionHistory, Recommendation
from backend.app.schemas import (
    UserCreate, UserOut, Token, UserLogin,
    SupplierCreate, SupplierUpdate, SupplierOut,
    PredictionCreate, PredictionOut,
    RecommendationResponse, DashboardResponse
)
from backend.app.services.auth import AuthService
from backend.app.services.supplier import SupplierService
from backend.app.services.prediction import PredictionService
from backend.app.services.recommendation import RecommendationService
from backend.app.services.dashboard import DashboardService

router = APIRouter()

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password and create user
    hashed_pwd = AuthService.hash_password(user_data.password)
    new_user = User(username=user_data.username, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not AuthService.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token
    access_token = AuthService.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(AuthService.get_current_user)):
    return current_user


# ==========================================
# SUPPLIER ENDPOINTS
# ==========================================

@router.get("/suppliers")
def get_suppliers(
    search: Optional[str] = Query(None, description="Search by supplier name, product or country"),
    country: Optional[str] = Query(None, description="Filter by country"),
    product_name: Optional[str] = Query(None, description="Filter by product name"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_dir: str = Query("asc", description="Sort direction (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    suppliers, total = SupplierService.get_suppliers(
        db, search, country, product_name, sort_by, sort_dir, page, limit
    )
    return {
        "suppliers": [SupplierOut.model_validate(s) for s in suppliers],
        "total": total,
        "page": page,
        "limit": limit
    }


@router.get("/suppliers/{id}", response_model=SupplierOut)
def get_supplier(id: int, db: Session = Depends(get_db), current_user: User = Depends(AuthService.get_current_user)):
    supplier = SupplierService.get_supplier_by_id(db, id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.post("/suppliers", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(
    supplier_data: SupplierCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Log adding supplier as an activity
    supplier = SupplierService.create_supplier(db, supplier_data)
    return supplier


@router.put("/suppliers/{id}", response_model=SupplierOut)
def update_supplier(
    id: int, 
    update_data: SupplierUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    supplier = SupplierService.update_supplier(db, id, update_data)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.delete("/suppliers/{id}")
def delete_supplier(id: int, db: Session = Depends(get_db), current_user: User = Depends(AuthService.get_current_user)):
    success = SupplierService.delete_supplier(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted successfully"}


# ==========================================
# PREDICTION ENDPOINT
# ==========================================

@router.post("/predict", response_model=PredictionOut)
def predict_freight(
    data: PredictionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    prediction = PredictionService.predict_freight(db, current_user.id, data)
    return prediction


# ==========================================
# RECOMMENDATION ENDPOINT
# ==========================================

@router.get("/recommendation", response_model=RecommendationResponse)
def get_recommendation(
    product_name: str = Query(..., description="Name of the product to procure"),
    origin: str = Query(..., description="Route starting city"),
    destination: str = Query(..., description="Route destination city"),
    distance: float = Query(..., gt=0, description="Route distance in km"),
    fuel_price: float = Query(..., gt=0, description="Current fuel price per liter"),
    month: str = Query(..., description="Month of shipment"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    prediction_data = PredictionCreate(
        origin=origin,
        destination=destination,
        distance=distance,
        fuel_price=fuel_price,
        month=month
    )
    
    response = RecommendationService.get_recommendation(
        db, current_user.id, product_name, prediction_data
    )
    return response


# ==========================================
# HISTORY ENDPOINTS
# ==========================================

@router.get("/history")
def get_history(
    search: Optional[str] = Query(None, description="Search by origin, destination or supplier name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Fetch predictions history for current user
    pred_query = db.query(PredictionHistory).filter(PredictionHistory.user_id == current_user.id)
    if search:
        search_pattern = f"%{search}%"
        pred_query = pred_query.filter(
            (PredictionHistory.origin.ilike(search_pattern)) | 
            (PredictionHistory.destination.ilike(search_pattern))
        )
    predictions = pred_query.order_by(PredictionHistory.created_at.desc()).all()

    # Fetch recommendations history for current user
    rec_query = db.query(Recommendation).filter(Recommendation.user_id == current_user.id)
    recommendations = rec_query.order_by(Recommendation.created_at.desc()).all()
    
    # Filter recommendations based on search term in nested supplier name if provided
    filtered_recs = []
    for r in recommendations:
        if search:
            match = False
            if r.supplier and search.lower() in r.supplier.name.lower():
                match = True
            if r.prediction and (search.lower() in r.prediction.origin.lower() or search.lower() in r.prediction.destination.lower()):
                match = True
            if match:
                filtered_recs.append(r)
        else:
            filtered_recs.append(r)

    # Format recommendations output with custom fields
    formatted_recs = []
    for r in filtered_recs:
        formatted_recs.append({
            "id": r.id,
            "total_landed_cost": r.total_landed_cost,
            "product_cost": r.product_cost,
            "predicted_freight_cost": r.predicted_freight_cost,
            "risk_premium": r.risk_premium,
            "created_at": r.created_at,
            "prediction": {
                "id": r.prediction.id if r.prediction else None,
                "origin": r.prediction.origin if r.prediction else "N/A",
                "destination": r.prediction.destination if r.prediction else "N/A",
                "distance": r.prediction.distance if r.prediction else 0.0,
                "fuel_price": r.prediction.fuel_price if r.prediction else 0.0,
                "month": r.prediction.month if r.prediction else "N/A",
                "predicted_freight_cost": r.prediction.predicted_freight_cost if r.prediction else 0.0,
                "confidence_score": r.prediction.confidence_score if r.prediction else 0.0,
            } if r.prediction else None,
            "supplier": {
                "id": r.supplier.id if r.supplier else None,
                "name": r.supplier.name if r.supplier else "N/A",
                "country": r.supplier.country if r.supplier else "N/A",
                "product_name": r.supplier.product_name if r.supplier else "N/A",
                "product_cost": r.supplier.product_cost if r.supplier else 0.0,
                "delivery_time": r.supplier.delivery_time if r.supplier else 0,
                "quality_rating": r.supplier.quality_rating if r.supplier else 0.0,
                "late_deliveries": r.supplier.late_deliveries if r.supplier else 0,
                "experience": r.supplier.experience if r.supplier else 0,
                "contact_info": r.supplier.contact_info if r.supplier else "N/A"
            } if r.supplier else None
        })

    return {
        "predictions": [PredictionOut.model_validate(p) for p in predictions],
        "recommendations": formatted_recs
    }


@router.delete("/history/prediction/{id}")
def delete_prediction(id: int, db: Session = Depends(get_db), current_user: User = Depends(AuthService.get_current_user)):
    pred = db.query(PredictionHistory).filter(PredictionHistory.id == id, PredictionHistory.user_id == current_user.id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    db.delete(pred)
    db.commit()
    return {"message": "Prediction deleted successfully"}


@router.delete("/history/recommendation/{id}")
def delete_recommendation(id: int, db: Session = Depends(get_db), current_user: User = Depends(AuthService.get_current_user)):
    rec = db.query(Recommendation).filter(Recommendation.id == id, Recommendation.user_id == current_user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    db.delete(rec)
    db.commit()
    return {"message": "Recommendation deleted successfully"}


# ==========================================
# DASHBOARD ENDPOINT
# ==========================================

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(AuthService.get_current_user)):
    dashboard_data = DashboardService.get_dashboard_data(db)
    return dashboard_data
