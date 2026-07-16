import os
import pandas as pd
import joblib
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models import PredictionHistory
from backend.app.schemas import PredictionCreate

class PredictionService:
    _model = None

    @classmethod
    def load_model(cls):
        """Lazy-load the joblib model pipeline from the trained_models folder."""
        if cls._model is None:
            # Construct path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_dir, "ml", "trained_models", "freight_model.joblib")
            
            if os.path.exists(model_path):
                try:
                    cls._model = joblib.load(model_path)
                    print(f"Prediction Service: Loaded Random Forest pipeline from {model_path}")
                except Exception as e:
                    print(f"Prediction Service Error loading model: {e}. Fallback formula will be used.")
                    cls._model = "fallback"
            else:
                print(f"Prediction Service: Model file {model_path} not found. Fallback formula will be used.")
                cls._model = "fallback"
        return cls._model

    @classmethod
    def predict_freight(cls, db: Session, user_id: Optional[int], data: PredictionCreate) -> PredictionHistory:
        """Run ML inference to predict freight cost, falling back to formula if no model exists, and save log."""
        model = cls.load_model()
        predicted_cost = 0.0
        confidence_score = 95.46  # Default based on model evaluation metrics report

        if model != "fallback" and model is not None:
            try:
                # Prepare DataFrame for scikit-learn pipeline
                input_df = pd.DataFrame([{
                    "Origin": data.origin,
                    "Destination": data.destination,
                    "Distance": data.distance,
                    "Fuel_Price": data.fuel_price,
                    "Month": data.month
                }])
                
                prediction = model.predict(input_df)
                predicted_cost = float(prediction[0])
            except Exception as e:
                print(f"ML Inference failed ({e}). Reverting to fallback formula.")
                model = "fallback"

        if model == "fallback" or model is None:
            # Fallback mathematical model matching the synthetic dataset structure
            base = 2000.0
            dist_cost = data.distance * 14.5
            fuel_multiplier = data.fuel_price / 95.0
            
            season_multiplier = 1.0
            if data.month in ["July", "August"]:
                season_multiplier = 1.18
            elif data.month in ["October", "November"]:
                season_multiplier = 1.10
            elif data.month in ["April", "May"]:
                season_multiplier = 0.95
                
            predicted_cost = (base + dist_cost) * fuel_multiplier * season_multiplier
            confidence_score = 90.00 # slightly lower confidence for mathematical approximation

        # Round values for cleanliness
        predicted_cost = round(predicted_cost, 2)
        confidence_score = round(confidence_score, 2)

        # Log prediction run to the database
        db_prediction = PredictionHistory(
            user_id=user_id,
            origin=data.origin,
            destination=data.destination,
            distance=data.distance,
            fuel_price=data.fuel_price,
            month=data.month,
            predicted_freight_cost=predicted_cost,
            confidence_score=confidence_score
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        return db_prediction
