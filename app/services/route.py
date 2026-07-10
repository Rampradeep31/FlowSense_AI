import math
import logging
import httpx
from typing import List, Tuple, Dict, Any
from app.config import settings

import json
from app.services.cache import cache_service

logger = logging.getLogger(__name__)

def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees lon, lat)
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    
    R = 6371.0  # Earth radius in kilometers
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

class RouteService:
    async def analyze_route(self, waypoints: List[List[float]]) -> Dict[str, Any]:
        """
        Analyzes route waypoints [[lon, lat], [lon, lat], ...]
        Returns distance (km), duration (hours), geometry (polyline), and waypoints.
        """
        if len(waypoints) < 2:
            raise ValueError("At least 2 waypoints are required to analyze a route.")

        # Coordinate format for OSRM: lon,lat;lon,lat;...
        coord_strs = [f"{wp[0]},{wp[1]}" for wp in waypoints]
        coord_path = ";".join(coord_strs)
        url = f"{settings.OSRM_BASE_URL.rstrip('/')}/route/v1/driving/{coord_path}?overview=full&geometries=polyline"

        # Check cache first
        cache_key = f"route_analysis:{coord_path}"
        try:
            cached_result = await cache_service.get(cache_key)
            if cached_result:
                logger.info("Returning cached route analysis.")
                return json.loads(cached_result)
        except Exception as e:
            logger.warning(f"Cache lookup failed for route: {e}")

        result = None
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == "Ok" and data.get("routes"):
                        route_data = data["routes"][0]
                        distance_meters = route_data.get("distance", 0.0)
                        duration_seconds = route_data.get("duration", 0.0)
                        geometry = route_data.get("geometry", "")
                        
                        result = {
                            "distance_km": round(distance_meters / 1000.0, 2),
                            "duration_hours": round(duration_seconds / 3600.0, 2),
                            "geometry": geometry,
                            "waypoints": waypoints
                        }
                    else:
                        logger.warning(f"OSRM returned non-ok status: {data.get('code')}")
                else:
                    logger.warning(f"OSRM returned status code: {response.status_code}")
        except Exception as e:
            logger.warning(f"OSRM request failed or timed out: {e}")

        # Fallback to simulated route calculation if external request failed
        if not result:
            logger.info("Falling back to simulated route analysis.")
            result = self._simulate_route(waypoints)

        # Cache the final result (whether live or simulated) for 24 hours
        try:
            await cache_service.set(cache_key, json.dumps(result), 86400)
        except Exception as e:
            logger.warning(f"Failed to cache route analysis: {e}")

        return result

    def _simulate_route(self, waypoints: List[List[float]]) -> Dict[str, Any]:
        total_dist_km = 0.0
        for i in range(len(waypoints) - 1):
            total_dist_km += haversine_distance(
                (waypoints[i][0], waypoints[i][1]),
                (waypoints[i+1][0], waypoints[i+1][1])
            )
        
        # Real-world driving distance in India is typically 1.3x of direct distance
        driving_distance_km = round(total_dist_km * 1.3, 2)
        
        # Average speed of 50 km/h (accounts for traffic, ghats, city entry/exit)
        average_speed_kmh = 50.0
        duration_hours = round(driving_distance_km / average_speed_kmh, 2)
        
        # Mock polyline geometry
        mock_geometry = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
        
        return {
            "distance_km": driving_distance_km,
            "duration_hours": duration_hours,
            "geometry": mock_geometry,
            "waypoints": waypoints
        }

route_service = RouteService()
