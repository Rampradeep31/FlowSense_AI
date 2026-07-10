import pytest
import datetime
from httpx import AsyncClient
from app.services.websocket import manager

@pytest.mark.anyio
async def test_crud_entities(client: AsyncClient):
    # Create Product
    prod_payload = {
        "name": "Insulin Test",
        "temp_min_c": 2.0,
        "temp_max_c": 8.0,
        "max_excursion_duration_minutes": 30,
        "max_delay_hours": 24.0
    }
    response = await client.post("/api/v1/products", json=prod_payload)
    assert response.status_code == 201
    prod_data = response.json()
    assert prod_data["name"] == "Insulin Test"

    # Create Cold Box
    box_payload = {
        "id": "BOX-CRUD-100",
        "model": "Chiller-X",
        "age_months": 12,
        "status": "active"
    }
    response = await client.post("/api/v1/cold-boxes", json=box_payload)
    assert response.status_code == 201
    box_data = response.json()
    assert box_data["id"] == "BOX-CRUD-100"

    # Create Carrier
    carrier_payload = {
        "name": "Logistics Carrier A",
        "reliability_pct": 98.0
    }
    response = await client.post("/api/v1/carriers", json=carrier_payload)
    assert response.status_code == 201
    carrier_data = response.json()
    assert carrier_data["name"] == "Logistics Carrier A"

@pytest.mark.anyio
async def test_shipment_creation_and_autoroute(client: AsyncClient):
    # Create self-contained entities
    prod_resp = await client.post("/api/v1/products", json={
        "name": "Product Auto",
        "temp_min_c": 2.0,
        "temp_max_c": 8.0,
        "max_excursion_duration_minutes": 30,
        "max_delay_hours": 24.0
    })
    prod_id = prod_resp.json()["id"]

    await client.post("/api/v1/cold-boxes", json={
        "id": "BOX-AUTO",
        "model": "Chiller-Auto",
        "age_months": 6,
        "status": "active"
    })

    carrier_resp = await client.post("/api/v1/carriers", json={
        "name": "Carrier Auto",
        "reliability_pct": 99.0
    })
    carrier_id = carrier_resp.json()["id"]

    # Create Shipment from Mumbai to Pune (triggers route linkage)
    shipment_payload = {
        "origin": "Mumbai",
        "destination": "Pune",
        "product_id": prod_id,
        "quantity": 500,
        "cold_box_id": "BOX-AUTO",
        "carrier_id": carrier_id,
        "departure_time": datetime.datetime.utcnow().isoformat()
    }

    response = await client.post("/api/v1/shipments", json=shipment_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["origin"] == "Mumbai"
    assert data["status"] == "in-transit"
    assert data["route_id"] is not None

@pytest.mark.anyio
async def test_rules_engine_temp_breach(client: AsyncClient):
    # Create self-contained entities
    prod_resp = await client.post("/api/v1/products", json={
        "name": "Product Temp",
        "temp_min_c": 2.0,
        "temp_max_c": 8.0,
        "max_excursion_duration_minutes": 30,
        "max_delay_hours": 24.0
    })
    prod_id = prod_resp.json()["id"]

    await client.post("/api/v1/cold-boxes", json={
        "id": "BOX-TEMP",
        "model": "Chiller-Temp",
        "age_months": 18,
        "status": "active"
    })

    carrier_resp = await client.post("/api/v1/carriers", json={
        "name": "Carrier Temp",
        "reliability_pct": 97.0
    })
    carrier_id = carrier_resp.json()["id"]

    # Create Shipment departing 5 hours ago so simulated readings fall inside the transit window
    departure_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    shipment_payload = {
        "origin": "Mumbai",
        "destination": "Pune",
        "product_id": prod_id,
        "quantity": 250,
        "cold_box_id": "BOX-TEMP",
        "carrier_id": carrier_id,
        "departure_time": departure_time.isoformat()
    }
    shipment_resp = await client.post("/api/v1/shipments", json=shipment_payload)
    shipment_id = shipment_resp.json()["id"]

    # Simulate a temperature excursion of 120 mins (exceeds 30 min threshold)
    sim_payload = {
        "cold_box_id": "BOX-TEMP",
        "shipment_id": str(shipment_id),
        "failing": True,
        "duration_minutes": 120,
        "interval_minutes": 5
    }
    sim_resp = await client.post("/api/v1/sensors/simulate", json=sim_payload)
    assert sim_resp.status_code == 201

    # Check status - should update to spoiled due to rules engine execution
    status_resp = await client.get(f"/api/v1/shipments/{shipment_id}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["shipment"]["status"] == "spoiled"

    # Check active alerts list
    alerts_resp = await client.get("/api/v1/alerts/active")
    alerts = alerts_resp.json()
    assert len(alerts) > 0
    temp_alert = [a for a in alerts if a["shipment_id"] == shipment_id and a["alert_type"] == "temp_breach"][0]
    assert temp_alert["severity"] == "critical"

    # Acknowledge the alert
    ack_payload = {"alert_id": temp_alert["id"]}
    ack_resp = await client.post("/api/v1/alerts/acknowledge", json=ack_payload)
    assert ack_resp.status_code == 200
    assert ack_resp.json()["is_acknowledged"] is True

@pytest.mark.anyio
async def test_rules_engine_delay_breach(client: AsyncClient):
    # Create a product with a short delay threshold (2 hours)
    prod_resp = await client.post("/api/v1/products", json={
        "name": "Highly Sensitive Vaccine",
        "temp_min_c": 2.0,
        "temp_max_c": 8.0,
        "max_excursion_duration_minutes": 30,
        "max_delay_hours": 2.0
    })
    prod_id = prod_resp.json()["id"]

    await client.post("/api/v1/cold-boxes", json={
        "id": "BOX-DELAY",
        "model": "Chiller-Delay",
        "age_months": 24,
        "status": "active"
    })

    carrier_resp = await client.post("/api/v1/carriers", json={
        "name": "Carrier Delay",
        "reliability_pct": 96.0
    })
    carrier_id = carrier_resp.json()["id"]

    # Create shipment departing 5 hours ago
    departure_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    shipment_payload = {
        "origin": "Mumbai",
        "destination": "Nashik",
        "product_id": prod_id,
        "quantity": 100,
        "cold_box_id": "BOX-DELAY",
        "carrier_id": carrier_id,
        "departure_time": departure_time.isoformat()
    }

    create_resp = await client.post("/api/v1/shipments", json=shipment_payload)
    shipment_id = create_resp.json()["id"]

    # Trigger Rules Engine check by simulating normal sensor logs
    sim_payload = {
        "cold_box_id": "BOX-DELAY",
        "shipment_id": str(shipment_id),
        "failing": False,
        "duration_minutes": 5,
        "interval_minutes": 5
    }
    await client.post("/api/v1/sensors/simulate", json=sim_payload)

    # Check status - should update to delayed
    status_resp = await client.get(f"/api/v1/shipments/{shipment_id}/status")
    status_data = status_resp.json()
    assert status_data["shipment"]["status"] == "delayed"

    # Check active alerts list
    alerts_resp = await client.get("/api/v1/alerts/active")
    alerts = alerts_resp.json()
    delay_alerts = [a for a in alerts if a["shipment_id"] == shipment_id and a["alert_type"] == "delay_breach"]
    assert len(delay_alerts) == 1
    assert delay_alerts[0]["severity"] == "critical"

@pytest.mark.anyio
async def test_websocket_broadcast_logic():
    # Verify ConnectionManager accepts, registers, and broadcasts correctly
    class MockWebSocket:
        def __init__(self) -> None:
            self.accepted = False
            self.sent_messages = []

        async def accept(self) -> None:
            self.accepted = True

        async def send_text(self, text: str) -> None:
            self.sent_messages.append(text)

    ws = MockWebSocket()
    await manager.connect(ws)  # type: ignore
    assert ws.accepted is True
    assert ws in manager.active_connections

    alert_payload = {"alert": "critical temp excursion"}
    await manager.broadcast_alert(alert_payload)
    assert len(ws.sent_messages) == 1
    assert "critical temp excursion" in ws.sent_messages[0]

    manager.disconnect(ws)  # type: ignore
    assert ws not in manager.active_connections
