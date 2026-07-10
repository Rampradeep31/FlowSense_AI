import pytest
import datetime
from httpx import AsyncClient

@pytest.mark.anyio
async def test_what_if_and_recommendations(client: AsyncClient):
    # 1. Create base entities (Product, 2 Cold Boxes, 2 Carriers)
    prod_resp = await client.post("/api/v1/products", json={
        "name": "Simulate Vaccine",
        "temp_min_c": 2.0,
        "temp_max_c": 8.0,
        "max_excursion_duration_minutes": 30,
        "max_delay_hours": 12.0
    })
    prod_id = prod_resp.json()["id"]

    # Cold Box 1 (Old)
    await client.post("/api/v1/cold-boxes", json={
        "id": "BOX-SIM-OLD",
        "model": "Standard-Chiller",
        "age_months": 22,
        "status": "active"
    })
    
    # Cold Box 2 (New, better insulation)
    await client.post("/api/v1/cold-boxes", json={
        "id": "BOX-SIM-NEW",
        "model": "Standard-Chiller",
        "age_months": 2,
        "status": "active"
    })

    # Carrier 1 (Standard reliability)
    carrier1_resp = await client.post("/api/v1/carriers", json={
        "name": "Logistics Standard",
        "reliability_pct": 80.0
    })
    carrier1_id = carrier1_resp.json()["id"]

    # Carrier 2 (Premium reliability)
    carrier2_resp = await client.post("/api/v1/carriers", json={
        "name": "Logistics Premium",
        "reliability_pct": 98.0
    })
    carrier2_id = carrier2_resp.json()["id"]

    # Create Shipment (departed 5 hours ago, using old cold box and standard carrier)
    departure_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    shipment_payload = {
        "origin": "Mumbai",
        "destination": "Pune",
        "product_id": prod_id,
        "quantity": 100,
        "cold_box_id": "BOX-SIM-OLD",
        "carrier_id": carrier1_id,
        "departure_time": departure_time.isoformat()
    }
    shipment_resp = await client.post("/api/v1/shipments", json=shipment_payload)
    assert shipment_resp.status_code == 201
    shipment_id = shipment_resp.json()["id"]

    # 2. Run What-If Simulation for Carrier override
    what_if_payload = {
        "shipment_id": shipment_id,
        "carrier_id": carrier2_id
    }
    resp = await client.post("/api/v1/simulation/what-if", json=what_if_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["shipment_id"] == shipment_id
    # Premium carrier should reduce delay, so delay reduction should be positive
    assert data["delay_reduction_hours"] > 0.0
    assert len(data["shap_explanations"]) == 3

    # 3. Run What-If Simulation for Cold Box override
    what_if_payload_box = {
        "shipment_id": shipment_id,
        "cold_box_id": "BOX-SIM-NEW"
    }
    resp_box = await client.post("/api/v1/simulation/what-if", json=what_if_payload_box)
    assert resp_box.status_code == 200
    data_box = resp_box.json()
    # Newer cold box should insulate better, so spoilage reduction should be positive
    assert data_box["spoilage_reduction_pct"] > 0.0

    # 4. Get Automated Optimization Recommendations
    rec_resp = await client.get(f"/api/v1/simulation/recommendations/{shipment_id}")
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert rec_data["shipment_id"] == shipment_id
    assert len(rec_data["recommendations"]) > 0

    # Verify formatting and sorting order
    recs = rec_data["recommendations"]
    for r in recs:
        assert r["type"] in ["carrier_upgrade", "box_upgrade", "departure_shift"]
        assert r["description"] != ""
        assert "actionable_details" in r

    # Verify sorted in descending order of spoilage reduction primarily
    for i in range(len(recs) - 1):
        assert recs[i]["predicted_spoilage_reduction_pct"] >= recs[i+1]["predicted_spoilage_reduction_pct"]

@pytest.mark.anyio
async def test_simulation_error_handling(client: AsyncClient):
    # Test invalid shipment on What-If
    resp = await client.post("/api/v1/simulation/what-if", json={"shipment_id": 99999, "carrier_id": 1})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]

    # Test invalid shipment on Recommendations
    resp = await client.get("/api/v1/simulation/recommendations/99999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]
