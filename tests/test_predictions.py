import pytest
import datetime
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.demand import DemandForecast

@pytest.mark.anyio
async def test_predictions_flow(client: AsyncClient, db: AsyncSession):
    # 1. Create base entities (Product, ColdBox, Carrier)
    prod_resp = await client.post("/api/v1/products", json={
        "name": "Predict Vaccine A",
        "temp_min_c": 2.0,
        "temp_max_c": 8.0,
        "max_excursion_duration_minutes": 30,
        "max_delay_hours": 12.0
    })
    assert prod_resp.status_code == 201
    prod_id = prod_resp.json()["id"]

    await client.post("/api/v1/cold-boxes", json={
        "id": "BOX-PRED-99",
        "model": "Chiller-Pred",
        "age_months": 15,
        "status": "active"
    })

    carrier_resp = await client.post("/api/v1/carriers", json={
        "name": "Carrier Pred",
        "reliability_pct": 92.0
    })
    assert carrier_resp.status_code == 201
    carrier_id = carrier_resp.json()["id"]

    # Create Shipment (departed 5 hours ago so simulated readings fall inside transit window)
    departure_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    shipment_payload = {
        "origin": "Mumbai",
        "destination": "Pune",
        "product_id": prod_id,
        "quantity": 100,
        "cold_box_id": "BOX-PRED-99",
        "carrier_id": carrier_id,
        "departure_time": departure_time.isoformat()
    }
    shipment_resp = await client.post("/api/v1/shipments", json=shipment_payload)
    assert shipment_resp.status_code == 201
    shipment_id = shipment_resp.json()["id"]

    # 2. Test Delay Prediction
    delay_payload = {"shipment_id": shipment_id}
    delay_resp = await client.post("/api/v1/predictions/delay", json=delay_payload)
    assert delay_resp.status_code == 200
    delay_data = delay_resp.json()
    
    assert delay_data["shipment_id"] == shipment_id
    assert delay_data["predicted_delay_hours"] >= 0.0
    assert 0.0 <= delay_data["delay_probability"] <= 1.0
    
    # Verify SHAP efficiency property: sum(shap) == predicted_delay_hours - base_value
    shap_sum = sum(item["shap_value"] for item in delay_data["shap_explanations"])
    diff = delay_data["predicted_delay_hours"] - delay_data["base_value"]
    assert abs(shap_sum - diff) < 1e-2

    # 3. Test Spoilage Prediction
    spoilage_payload = {"shipment_id": shipment_id}
    spoilage_resp = await client.post("/api/v1/predictions/spoilage", json=spoilage_payload)
    assert spoilage_resp.status_code == 200
    spoilage_data = spoilage_resp.json()

    assert spoilage_data["shipment_id"] == shipment_id
    assert 0.0 <= spoilage_data["spoilage_probability"] <= 1.0
    assert spoilage_data["risk_category"] in ["low", "medium", "high"]

    # Verify SHAP efficiency property for logistic non-linear model: sum(shap) == spoilage_probability - base_value
    shap_sum_spoil = sum(item["shap_value"] for item in spoilage_data["shap_explanations"])
    diff_spoil = spoilage_data["spoilage_probability"] - spoilage_data["base_value"]
    assert abs(shap_sum_spoil - diff_spoil) < 1e-3

    # 4. Test Demand Forecasting
    demand_payload = {
        "product_id": prod_id,
        "destination": "Nashik",
        "forecast_days": 7
    }
    demand_resp = await client.post("/api/v1/predictions/demand", json=demand_payload)
    assert demand_resp.status_code == 200
    demand_data = demand_resp.json()

    assert demand_data["product_id"] == prod_id
    assert demand_data["destination"] == "Nashik"
    assert len(demand_data["forecast"]) == 7
    assert demand_data["total_forecasted"] == sum(item["quantity"] for item in demand_data["forecast"])

    # Verify SHAP efficiency property for multiplicative demand model (allowing up to 7.0 units for daily integer rounding)
    shap_sum_demand = sum(item["shap_value"] for item in demand_data["shap_explanations"])
    diff_demand = demand_data["total_forecasted"] - demand_data["base_value"]
    assert abs(shap_sum_demand - diff_demand) <= 7.0

    # Verify daily forecasts were written to the database
    # Check directly using select query inside transaction
    stmt = select(DemandForecast).where(
        DemandForecast.product_id == prod_id,
        DemandForecast.destination == "Nashik"
    )
    res = await db.execute(stmt)
    forecasts_in_db = res.scalars().all()
    assert len(forecasts_in_db) == 7

@pytest.mark.anyio
async def test_predictions_error_handling(client: AsyncClient):
    # Test missing shipment delay prediction
    resp = await client.post("/api/v1/predictions/delay", json={"shipment_id": 99999})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]

    # Test missing shipment spoilage prediction
    resp = await client.post("/api/v1/predictions/spoilage", json={"shipment_id": 99999})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]

    # Test missing product demand forecast
    resp = await client.post("/api/v1/predictions/demand", json={"product_id": 99999, "destination": "Pune"})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]
