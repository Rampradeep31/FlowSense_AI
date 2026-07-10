import pytest
import time
from httpx import AsyncClient
from app.services.cache import cache_service

@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.anyio
async def test_route_analyze(client: AsyncClient):
    payload = {
        "waypoints": [
            [72.8777, 19.0760],  # Mumbai
            [73.8567, 18.5204]   # Pune
        ]
    }
    start_time = time.time()
    response = await client.post("/api/v1/route/analyze", json=payload)
    end_time = time.time()
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "distance_km" in data
    assert "duration_hours" in data
    assert "geometry" in data
    assert data["distance_km"] > 0
    assert data["duration_hours"] > 0
    
    # Verify response time is within the 3-second limit
    assert (end_time - start_time) < 3.0

@pytest.mark.anyio
async def test_weather_forecast(client: AsyncClient):
    # Pre-create a route to test route ID references
    route_payload = {
        "waypoints": [
            [72.8777, 19.0760],
            [73.8567, 18.5204]
        ]
    }
    route_resp = await client.post("/api/v1/route/analyze", json=route_payload)
    assert route_resp.status_code == 201
    route_id = route_resp.json()["id"]

    weather_payload = {
        "route_id": route_id
    }
    
    start_time = time.time()
    response = await client.post("/api/v1/weather/forecast", json=weather_payload)
    end_time = time.time()
    
    assert response.status_code == 200
    data = response.json()
    assert "forecasts" in data
    assert len(data["forecasts"]) == 2
    
    first_wp = data["forecasts"][0]
    assert "waypoint_index" in first_wp
    assert "forecast" in first_wp
    assert len(first_wp["forecast"]) > 0
    assert "temp_c" in first_wp["forecast"][0]
    assert "humidity_pct" in first_wp["forecast"][0]
    assert "precipitation_mm" in first_wp["forecast"][0]
    
    assert (end_time - start_time) < 3.0

@pytest.mark.anyio
async def test_weather_caching(client: AsyncClient):
    await cache_service.clear()
    payload = {
        "waypoints": [
            [72.8777, 19.0760],
            [73.8567, 18.5204]
        ]
    }
    
    # First call triggers simulation/fetch
    resp1 = await client.post("/api/v1/weather/forecast", json=payload)
    assert resp1.status_code == 200
    
    # Second call should pull directly from cache
    start_time = time.time()
    resp2 = await client.post("/api/v1/weather/forecast", json=payload)
    end_time = time.time()
    
    assert resp2.status_code == 200
    # Cache hit should return almost instantly (< 100ms)
    assert (end_time - start_time) < 0.1
    assert resp1.json() == resp2.json()

@pytest.mark.anyio
async def test_news_disruptions(client: AsyncClient):
    payload = {
        "waypoints": [
            [72.8777, 19.0760],  # Mumbai
            [73.3644, 18.7602],  # Khandala (triggers expressway mock landslide hotspot)
            [73.8567, 18.5204]   # Pune
        ],
        "radius_km": 50.0
    }
    
    start_time = time.time()
    response = await client.post("/api/v1/news/disruptions", json=payload)
    end_time = time.time()
    
    assert response.status_code == 200
    data = response.json()
    assert "disruptions" in data
    assert len(data["disruptions"]) > 0
    
    first_news = data["disruptions"][0]
    assert "title" in first_news
    assert "severity" in first_news
    assert "distance_from_route_km" in first_news
    assert first_news["distance_from_route_km"] <= 50.0
    
    assert (end_time - start_time) < 3.0

@pytest.mark.anyio
async def test_sensors_simulate(client: AsyncClient):
    # 1. Healthy Cold Box Simulation
    payload_healthy = {
        "cold_box_id": "BOX-TEST-NORMAL",
        "failing": False,
        "duration_minutes": 60,
        "interval_minutes": 10
    }
    
    response = await client.post("/api/v1/sensors/simulate", json=payload_healthy)
    assert response.status_code == 201
    data = response.json()
    assert "readings" in data
    readings = data["readings"]
    assert len(readings) == 6
    
    for r in readings:
        assert 2.0 <= r["temperature_c"] <= 8.0
        assert r["cold_box_id"] == "BOX-TEST-NORMAL"
        
    # 2. Failing Cold Box Simulation
    payload_failing = {
        "cold_box_id": "BOX-TEST-FAILED",
        "failing": True,
        "duration_minutes": 60,
        "interval_minutes": 10
    }
    
    response_fail = await client.post("/api/v1/sensors/simulate", json=payload_failing)
    assert response_fail.status_code == 201
    readings_fail = response_fail.json()["readings"]
    assert len(readings_fail) == 6
    
    # Verify temperature climbs and spikes up to near 15°C
    temperatures = [r["temperature_c"] for r in readings_fail]
    assert temperatures[-1] >= 12.0
