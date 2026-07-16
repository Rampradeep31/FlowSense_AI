from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base
from backend.app.api.endpoints import router as api_router

# Initialize Database tables if SQLite is used
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully or verified.")
except Exception as e:
    print(f"Error initializing database: {e}")

# Initialize FastAPI App
app = FastAPI(
    title="FlowSense AI: Smart Procurement and Freight Cost Prediction System",
    description="An explainable AI decision support system for logistics cost estimation and supplier risk auditing.",
    version="1.0.0"
)

# Configure CORS Middleware
# Allows the React frontend running on port 5173 or other local client to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api")

# Welcome Endpoint
@app.get("/")
def read_root():
    return {
        "project": "FlowSense AI: Smart Procurement and Freight Cost Prediction System",
        "system_type": "Explainable AI Decision Support System",
        "documentation": "/docs",
        "status": "Online"
    }
