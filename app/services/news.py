import logging
import httpx
import datetime
from typing import List, Dict, Any
from app.config import settings
from app.services.cache import cache_service
from app.services.route import haversine_distance
import json

logger = logging.getLogger(__name__)

# List of typical highway disruption hotspots in Maharashtra with coordinates
MOCK_DISRUPTIONS = [
    {
        "title": "Landslide at Khandala Ghat triggers traffic halt on Mumbai-Pune Expressway",
        "description": "Heavy monsoon rainfall triggered a massive landslide near Khandala Ghat. Highway authorities have temporarily suspended traffic towards Pune. Debris clearance is underway.",
        "source": "Maharashtra Highway Info",
        "url": "https://example.com/news/expressway-landslide",
        "longitude": 73.3644,
        "latitude": 18.7602,
        "severity": "high",
        "delay_offset_hours": 4.5
    },
    {
        "title": "Waterlogging in Kalyan causes traffic delays on Mumbai-Nashik highway",
        "description": "Severe waterlogging in low-lying areas of Kalyan and Bhiwandi has led to slow-moving traffic on National Highway 3. Commuters are advised to expect delays of up to 2 hours.",
        "source": "Thane Traffic Update",
        "url": "https://example.com/news/kalyan-waterlogging",
        "longitude": 73.1360,
        "latitude": 19.2403,
        "severity": "medium",
        "delay_offset_hours": 2.0
    },
    {
        "title": "Transporters strike impacts commercial vehicle movement at Mumbai entry points",
        "description": "A localized truck drivers' protest at Dahisar and Mulund toll plazas has caused container queuing. Police are monitoring the situation to keep emergency medical supplies moving.",
        "source": "Mumbai Mirror",
        "url": "https://example.com/news/toll-protest",
        "longitude": 72.8601,
        "latitude": 19.2505,
        "severity": "medium",
        "delay_offset_hours": 1.5
    },
    {
        "title": "Heavy fog reduces visibility to less than 10 meters on Kasara Ghat",
        "description": "Dense fog cover has descended on the Kasara Ghat section of the Mumbai-Nashik route. Drivers are urged to proceed with extreme caution and use hazard lights. High risk of delays.",
        "source": "National Highway Authority of India",
        "url": "https://example.com/news/kasara-fog",
        "longitude": 73.4783,
        "latitude": 19.6231,
        "severity": "low",
        "delay_offset_hours": 1.0
    },
    {
        "title": "Road repair works on Pune-Solapur highway (NH-65) near Hadapsar",
        "description": "Major resurfacing work on NH-65 has reduced traffic flow to a single lane near Hadapsar. Heavy traffic congestion reported. Peak hour delays expected for the next 3 days.",
        "source": "Pune Traffic Police",
        "url": "https://example.com/news/hadapsar-repair",
        "longitude": 73.9261,
        "latitude": 18.5089,
        "severity": "low",
        "delay_offset_hours": 0.5
    }
]

class NewsService:
    async def get_disruptions(self, waypoints: List[List[float]], radius_km: float = 50.0) -> List[Dict[str, Any]]:
        """
        Retrieves relevant news disruptions within the specified radius of the route.
        Caches results for 15 minutes.
        """
        # Create a unique key based on waypoints and radius
        coords_str = "_".join([f"{wp[0]},{wp[1]}" for wp in waypoints])
        cache_key = f"news_disruptions:{coords_str}:{radius_km}"
        
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            logger.info("Returning cached news disruptions.")
            return json.loads(cached_data)

        # Retrieve raw news from API or fallback
        all_news = await self._fetch_news()
        
        # Filter news that are within 50km of any route waypoint
        relevant_news = []
        for article in all_news:
            art_lat = article.get("latitude")
            art_lon = article.get("longitude")
            if art_lat is None or art_lon is None:
                continue
                
            # Check proximity to any waypoint
            is_close = False
            for wp in waypoints:
                dist = haversine_distance((wp[0], wp[1]), (art_lon, art_lat))
                if dist <= radius_km:
                    is_close = True
                    article["distance_from_route_km"] = round(dist, 1)
                    break
            
            if is_close:
                relevant_news.append(article)

        # Cache for 15 minutes
        await cache_service.set(cache_key, json.dumps(relevant_news), 900)
        return relevant_news

    async def _fetch_news(self) -> List[Dict[str, Any]]:
        """
        Fetches news from NewsAPI if key is available, else falls back to mock list.
        """
        if settings.NEWS_API_KEY:
            # Query about highway traffic, strikes, landslides or road closures in Maharashtra/Mumbai/Pune
            query = "road closure OR highway strike OR landslide OR flood Maharashtra"
            url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={settings.NEWS_API_KEY}"
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get("articles", [])
                        parsed_articles = []
                        # Process articles and assign coordinates based on city matches in titles/descriptions
                        for art in articles[:10]:
                            title = art.get("title", "")
                            description = art.get("description", "")
                            full_text = f"{title} {description}".lower()
                            
                            # Guess coordinates based on Maharashtra region matching
                            lat, lon = None, None
                            if "expressway" in full_text or "khandala" in full_text or "lonavala" in full_text:
                                lat, lon = 18.7602, 73.3644
                            elif "kalyan" in full_text or "bhiwandi" in full_text:
                                lat, lon = 19.2403, 73.1360
                            elif "kasara" in full_text or "igatpuri" in full_text:
                                lat, lon = 19.6231, 73.4783
                            elif "pune" in full_text:
                                lat, lon = 18.5204, 73.8567
                            elif "mumbai" in full_text:
                                lat, lon = 19.0760, 72.8777
                            else:
                                # Default to central highway point
                                lat, lon = 19.0, 73.0
                            
                            published_at = art.get("publishedAt")
                            # Normalize published_at
                            if published_at:
                                published_at_str = published_at
                            else:
                                published_at_str = datetime.datetime.utcnow().isoformat()
                                
                            parsed_articles.append({
                                "title": title,
                                "description": description,
                                "source": art.get("source", {}).get("name", "NewsAPI"),
                                "url": art.get("url"),
                                "latitude": lat,
                                "longitude": lon,
                                "severity": "high" if any(k in full_text for k in ["landslide", "closed", "halt"]) else "medium",
                                "published_at": published_at_str
                            })
                        return parsed_articles
            except Exception as e:
                logger.warning(f"NewsAPI request failed: {e}")

        # Fallback to simulated regional disruptions
        logger.info("Using simulated news disruptions.")
        simulated_news = []
        now = datetime.datetime.utcnow()
        for idx, item in enumerate(MOCK_DISRUPTIONS):
            pub_time = now - datetime.timedelta(hours=idx * 6)
            simulated_news.append({
                "title": item["title"],
                "description": item["description"],
                "source": item["source"],
                "url": item["url"],
                "latitude": item["latitude"],
                "longitude": item["longitude"],
                "severity": item["severity"],
                "published_at": pub_time.isoformat()
            })
        return simulated_news

news_service = NewsService()
