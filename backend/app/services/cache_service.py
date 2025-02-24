from functools import lru_cache
from datetime import datetime, timedelta
import redis
from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger("cache_service")

class CacheService:
    _redis = redis.from_url(settings.REDIS_URL)
    
    @staticmethod
    async def set_cache(key: str, value: str, expire: int = None):
        try:
            if expire is None:
                expire = settings.CACHE_TTL
            CacheService._redis.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
    
    @staticmethod
    async def get_cache(key: str) -> str:
        try:
            return CacheService._redis.get(key)
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return None
    
    @staticmethod
    async def clear_cache(pattern: str = "*"):
        try:
            keys = CacheService._redis.keys(pattern)
            if keys:
                CacheService._redis.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear failed: {e}") 