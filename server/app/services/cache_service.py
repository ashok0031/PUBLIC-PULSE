"""
Redis-based caching service for API responses
"""
import os
import json
import logging
from typing import Optional, Any
from functools import wraps
from datetime import timedelta

logger = logging.getLogger(__name__)

# Try to import redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available. Caching will be disabled.")

class CacheService:
    """Service for caching API responses in Redis"""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = False
        
        if REDIS_AVAILABLE:
            try:
                redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                self.enabled = True
                logger.info("Redis cache service initialized successfully")
            except Exception as e:
                logger.warning(f"Redis cache not available: {e}. Using in-memory fallback.")
                self.enabled = False
        
        # In-memory fallback cache (simple dict with TTL)
        self._memory_cache = {}
        self._memory_cache_ttl = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self.enabled and self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Fallback to memory cache
        if key in self._memory_cache:
            import time
            if time.time() < self._memory_cache_ttl.get(key, 0):
                return self._memory_cache[key]
            else:
                # Expired
                del self._memory_cache[key]
                del self._memory_cache_ttl[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 120) -> bool:
        """Set value in cache with TTL"""
        if self.enabled and self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    ttl_seconds,
                    json.dumps(value, default=str)
                )
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        # Fallback to memory cache
        import time
        self._memory_cache[key] = value
        self._memory_cache_ttl[key] = time.time() + ttl_seconds
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if self.enabled and self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        # Fallback to memory cache
        if key in self._memory_cache:
            del self._memory_cache[key]
            del self._memory_cache_ttl[key]
        
        return True
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if self.enabled and self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis clear_pattern error: {e}")
        
        # Fallback: clear matching keys from memory
        import re
        regex = re.compile(pattern.replace('*', '.*'))
        count = 0
        for key in list(self._memory_cache.keys()):
            if regex.match(key):
                del self._memory_cache[key]
                if key in self._memory_cache_ttl:
                    del self._memory_cache_ttl[key]
                count += 1
        return count

# Global cache instance
cache_service = CacheService()

def cached(ttl_seconds: int = 120, key_prefix: str = "cache"):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            import hashlib
            key_str = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = f"{key_prefix}:{hashlib.md5(key_str.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl_seconds)
            return result
        
        return wrapper
    return decorator

