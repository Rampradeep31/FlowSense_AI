import logging
import httpx
import datetime
from typing import List, Dict, Any
from app.config import settings
from app.services.cache import cache_service
import json

logger = logging.getLogger(__name__)

class WeatherService:
    async def get_forecast(self, waypoints: List[List[float]]) -> List[Dict[str, Any]]:
        """
        Retrieves weather forecasts for the coordinates in the route.
        Caches the data for 1 hour.
        """
        # Create a unique key based on waypoints
        coords_str = "_".join([f"{wp[0]},{wp[1]}" for wp in waypoints])
        cache_key = f"weather_forecast:{coords_str}"
        
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            logger.info("Returning cached weather forecast.")
            return json.loads(cached_data)

        forecasts = []
        for idx, wp in enumerate(waypoints):
            lon, lat = wp[0], wp[1]
            wp_forecast = await self._fetch_waypoint_forecast(lat, lon, idx)
            forecasts.append(wp_forecast)

        # Cache for 1 hour
        await cache_service.set(cache_key, json.dumps(forecasts), 3600)
        return forecasts

    async def _fetch_waypoint_forecast(self, lat: float, lon: float, idx: int) -> Dict[str, Any]:
        if settings.OPENWEATHER_API_KEY:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        forecast_list = []
                        # Pick a subset of forecasts (e.g., first 8 intervals = 24 hours or every 12h for 5 days)
                        for item in data.get("list", [])[:10]:
                            dt_txt = item.get("dt_txt")
                            dt = datetime.datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S") if dt_txt else datetime.datetime.fromtimestamp(item.get("dt", 0))
                            main = item.get("main", {})
                            rain = item.get("rain", {}).get("3h", 0.0)
                            forecast_list.append({
                                "time": dt.isoformat(),
                                "temp_c": main.get("temp", 28.0),
                                "humidity_pct": main.get("humidity", 65.0),
                                "precipitation_mm": rain
                            })
                        return {
                            "waypoint_index": idx,
                            "latitude": lat,
                            "longitude": lon,
                            "forecast": forecast_list
                        }
                    else:
                        logger.warning(f"OpenWeather API returned status code {response.status_code} for ({lat}, {lon})")
            except Exception as e:
                logger.warning(f"OpenWeather request failed for ({lat}, {lon}): {e}")

        # Fallback to simulated weather forecast
        return self._simulate_waypoint_forecast(lat, lon, idx)

    def _simulate_waypoint_forecast(self, lat: float, lon: float, idx: int) -> Dict[str, Any]:
        forecast_list = []
        now = datetime.datetime.utcnow()
        
        # Generate weather for next 5 days, every 12 hours (10 intervals)
        for i in range(10):
            forecast_time = now + datetime.timedelta(hours=i * 12)
            # Monsoon is June to September in Maharashtra
            is_monsoon = 6 <= forecast_time.month <= 9
            is_day = 6 <= forecast_time.hour < 18
            
            # Base temperatures for Maharashtra (hot day, cooler night)
            temp = 33.0 if is_day else 24.0
            if is_monsoon:
                temp -= 3.0  # slightly cooler due to cloud cover/rain
                humidity = 88.0
                precipitation = 8.0 if i % 3 == 0 else 0.0  # periodic monsoon showers
            else:
                humidity = 50.0 if is_day else 70.0
                precipitation = 0.0

            forecast_list.append({
                "time": forecast_time.isoformat(),
                "temp_c": round(temp, 1),
                "humidity_pct": round(humidity, 1),
                "precipitation_mm": round(precipitation, 1)
            })

        return {
            "waypoint_index": idx,
            "latitude": lat,
            "longitude": lon,
            "forecast": forecast_list
        }

weather_service = WeatherService()
