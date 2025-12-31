"""Caching layer for frequently accessed data."""
from typing import Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Simple in-memory cache (can be replaced with Redis in production)
_cache: dict = {}
_cache_timestamps: dict = {}


class Cache:
    """Simple in-memory cache implementation."""
    
    def __init__(self, default_ttl: int = 60):
        """
        Initialize cache.
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None
        
        # Check if expired
        if key in self._timestamps:
            if datetime.utcnow() > self._timestamps[key]:
                del self._cache[key]
                del self._timestamps[key]
                return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        self._cache[key] = value
        ttl = ttl or self.default_ttl
        self._timestamps[key] = datetime.utcnow() + timedelta(seconds=ttl)
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
        self._timestamps.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        if key not in self._cache:
            return False
        
        if key in self._timestamps:
            if datetime.utcnow() > self._timestamps[key]:
                del self._cache[key]
                del self._timestamps[key]
                return False
        
        return True


# Global cache instance
cache = Cache(default_ttl=60)


def get_cache() -> Cache:
    """Get the global cache instance."""
    return cache
