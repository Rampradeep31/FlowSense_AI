import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

def train_model():
    # 1. Load Dataset
    dataset_path = "ml/datasets/freight_dataset.csv"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}. Please run generate_dataset.py first.")
        
    df = pd.read_csv(dataset_path)
    
    # 2. Separate features and target
    X = df[["Origin", "Destination", "Distance", "Fuel_Price", "Month"]]
    y = df["Freight_Cost"]
    
    # 3. Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Create Preprocessing Pipeline
    categorical_features = ["Origin", "Destination", "Month"]
    numerical_features = ["Distance", "Fuel_Price"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ]
    )
    
    # 5. Create Full Training Pipeline
    model_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
        ]
    )
    
    # 6. Train the model
    print("Training RandomForestRegressor model...")
    model_pipeline.fit(X_train, y_train)
    
    # 7. Evaluate the model
    y_pred = model_pipeline.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    # Calculate simple confidence score (mean absolute percentage accuracy)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    accuracy_percentage = max(0.0, min(100.0, 100.0 - mape))
    
    # Output metrics
    report = f"""====================================================
MODEL EVALUATION REPORT
====================================================
Model Type: Random Forest Regression Pipeline
Train Samples: {len(X_train)}
Test Samples: {len(X_test)}

Metrics:
- R-squared (R2) Score: {r2:.4f}
- Mean Absolute Error (MAE): Rs. {mae:.2f}
- Root Mean Squared Error (RMSE): Rs. {rmse:.2f}
- Mean Absolute Percentage Error (MAPE): {mape:.2f}%
- Prediction Confidence Score: {accuracy_percentage:.2f}%
====================================================
"""
    print(report)
    
    # 8. Save Model and metadata
    os.makedirs("ml/trained_models", exist_ok=True)
    model_save_path = "ml/trained_models/freight_model.joblib"
    joblib.dump(model_pipeline, model_save_path)
    print(f"Model pipeline saved successfully to {model_save_path}")
    
    # Save Report
    with open("ml/trained_models/accuracy_report.txt", "w") as f:
        f.write(report)
        
if __name__ == "__main__":
    train_model()
