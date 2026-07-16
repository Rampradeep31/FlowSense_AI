# FlowSense AI: Smart Procurement & Freight Cost Prediction System

FlowSense AI is an explainable AI-powered decision support system designed to optimize procurement landed costs. By integrating Random Forest regression models for freight charge prediction with supplier quality and reliability risk metrics, it enables procurement managers to identify and select the most cost-effective suppliers.

## Features

- **Freight Cost Prediction:** Machine learning regression pipeline (Random Forest) predicting freight costs based on origin, destination, distance, fuel prices, and season.
- **Supplier Risk Auditing:** Multi-criteria risk scoring for suppliers based on quality rating, delivery delays, and experience.
- **Landed Cost Optimization:** Interactive recommendations calculated dynamically by combining product cost, predicted freight charges, and calculated supplier risk premiums.
- **Interactive Dashboard:** Modern, responsive interface visualizing historical data, predictions, and real-time recommendations.

## Technical Architecture

- **Backend:** FastAPI (Python 3.10+), SQLAlchemy ORM (SQLite/PostgreSQL)
- **Frontend:** React (Vite, TypeScript, Tailwind CSS, Recharts)
- **ML Engine:** Scikit-Learn RandomForestRegressor pipeline

## Getting Started

1. Clone the repository.
2. Initialize and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install backend dependencies and seed the database:
   ```bash
   pip install -r backend/requirements.txt
   python backend/seed.py
   ```
4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
5. Start both servers using the startup script:
   ```powershell
   ./run_all.ps1
   ```
