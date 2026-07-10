import logging
import time
from typing import Dict, Optional, Tuple
from redis.asyncio import Redis, from_url
from app.config import settings

logger = logging.getLogger(__name__)

class InMemoryCache:
    def __init__(self) -> None:
        self._cache: Dict[str, Tuple[str, float]] = {}

    def get(self, key: str) -> Optional[str]:
        if key not in self._cache:
            return None
        value, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: str, expire: int) -> None:
        expiry = time.time() + expire
        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        self._cache.clear()


class CacheService:
    def __init__(self) -> None:
        self.redis: Optional[Redis] = None
        self.in_memory = InMemoryCache()
        self.use_redis = False

        if settings.REDIS_URL:
            try:
                self.redis = from_url(settings.REDIS_URL, decode_responses=True)
                self.use_redis = True
                logger.info("Initialized Redis cache configuration.")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache, falling back to In-Memory: {e}")
                self.use_redis = False
        else:
            logger.info("Redis not configured. Using In-Memory cache fallback.")

    async def get(self, key: str) -> Optional[str]:
        if self.use_redis and self.redis:
            try:
                return await self.redis.get(key)
            except Exception as e:
                logger.warning(f"Redis get error, falling back to In-Memory: {e}")
                # Temporarily disable Redis to avoid spamming connection errors
                self.use_redis = False
        return self.in_memory.get(key)

    async def set(self, key: str, value: str, expire: int) -> bool:
        if self.use_redis and self.redis:
            try:
                await self.redis.set(key, value, ex=expire)
                return True
            except Exception as e:
                logger.warning(f"Redis set error, falling back to In-Memory: {e}")
                self.use_redis = False
        self.in_memory.set(key, value, expire)
        return True

    async def delete(self, key: str) -> bool:
        if self.use_redis and self.redis:
            try:
                result = await self.redis.delete(key)
                return bool(result and result > 0)
            except Exception as e:
                logger.warning(f"Redis delete error, falling back to In-Memory: {e}")
                self.use_redis = False
        return self.in_memory.delete(key)

    async def clear(self) -> None:
        if self.use_redis and self.redis:
            try:
                await self.redis.flushdb()
            except Exception as e:
                logger.warning(f"Redis flushdb error: {e}")
        self.in_memory.clear()

cache_service = CacheService()
