import pytest
import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sensor import SensorReading

@pytest.mark.anyio
async def test_shipment_compliance_report(client: AsyncClient, db: AsyncSession):
    # 1. Create base entities
    prod_resp = await client.post("/api/v1/products", json={
        "name": "Audit Vaccine",
        "temp_min_c": 2.0,
        "temp_max_c": 8.0,
        "max_excursion_duration_minutes": 30,
        "max_delay_hours": 12.0
    })
    prod_id = prod_resp.json()["id"]

    await client.post("/api/v1/cold-boxes", json={
        "id": "BOX-AUD-1",
        "model": "Standard-Chiller",
        "age_months": 10,
        "status": "active"
    })

    carrier_resp = await client.post("/api/v1/carriers", json={
        "name": "Carrier Audits",
        "reliability_pct": 95.0
    })
    carrier_id = carrier_resp.json()["id"]

    # Create Shipment (departure 2 hours ago)
    departure_time = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    shipment_payload = {
        "origin": "Mumbai",
        "destination": "Nashik",
        "product_id": prod_id,
        "quantity": 200,
        "cold_box_id": "BOX-AUD-1",
        "carrier_id": carrier_id,
        "departure_time": departure_time.isoformat()
    }
    shipment_resp = await client.post("/api/v1/shipments", json=shipment_payload)
    shipment_id = shipment_resp.json()["id"]

    # 2. Add mock sensor readings creating a 25-minute temperature excursion
    # Normal temperature
    t0 = departure_time + datetime.timedelta(minutes=10)
    db.add(SensorReading(cold_box_id="BOX-AUD-1", shipment_id=str(shipment_id), timestamp=t0, temperature_c=5.0, humidity_pct=50.0))
    # Excursion begins
    t1 = t0 + datetime.timedelta(minutes=10)
    db.add(SensorReading(cold_box_id="BOX-AUD-1", shipment_id=str(shipment_id), timestamp=t1, temperature_c=12.0, humidity_pct=55.0))
    # Excursion peak
    t2 = t1 + datetime.timedelta(minutes=10)
    db.add(SensorReading(cold_box_id="BOX-AUD-1", shipment_id=str(shipment_id), timestamp=t2, temperature_c=14.0, humidity_pct=55.0))
    # Excursion returns to normal
    t3 = t2 + datetime.timedelta(minutes=15)
    db.add(SensorReading(cold_box_id="BOX-AUD-1", shipment_id=str(shipment_id), timestamp=t3, temperature_c=4.0, humidity_pct=50.0))
    
    await db.commit()

    # 3. Check shipment compliance report JSON
    rep_resp = await client.get(f"/api/v1/compliance/shipment/{shipment_id}/report")
    assert rep_resp.status_code == 200
    report = rep_resp.json()
    assert report["shipment_id"] == shipment_id
    assert report["compliance_status"] == "compliant"  # 25 min excursion < 30 max limit
    assert report["excursions_count"] == 1
    assert report["excursions"][0]["duration_minutes"] == 25.0
    assert report["excursions"][0]["max_temperature"] == 14.0
    assert report["excursions"][0]["min_temperature"] == 12.0
    assert report["estimated_loss_inr"] == 0.0

    # 4. Check CSV telemetry logs export
    exp_resp = await client.get(f"/api/v1/compliance/shipment/{shipment_id}/export")
    assert exp_resp.status_code == 200
    assert "text/csv" in exp_resp.headers["content-type"]
    assert "attachment" in exp_resp.headers["content-disposition"]
    body = exp_resp.text
    assert body.startswith("Timestamp,Temperature_C,Humidity_Pct,Excursion_Active,Safe_Min_C,Safe_Max_C")
    # Verify we have row details
    assert "12.0" in body
    assert "TRUE" in body
    assert "FALSE" in body

    # 5. Check monthly summary
    sum_resp = await client.get("/api/v1/compliance/summary")
    assert sum_resp.status_code == 200
    summary = sum_resp.json()
    assert summary["total_shipments_dispatched"] > 0
    assert len(summary["carrier_rankings"]) > 0

    # 6. Check summary CSV export
    sum_exp_resp = await client.get("/api/v1/compliance/summary/export")
    assert sum_exp_resp.status_code == 200
    assert "text/csv" in sum_exp_resp.headers["content-type"]
    assert sum_exp_resp.text.startswith("Shipment ID,Origin,Destination,Product Name,Carrier Name,Quantity Vials,Status,Estimated Loss INR,Departure Time")

@pytest.mark.anyio
async def test_compliance_error_handling(client: AsyncClient):
    # Test invalid shipment report
    resp = await client.get("/api/v1/compliance/shipment/99999/report")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]

    # Test invalid shipment export
    resp = await client.get("/api/v1/compliance/shipment/99999/export")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]
