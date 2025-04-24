import os
import json
import hashlib
import time
from datetime import datetime
from src.utils.config import CACHE_DIR, NEWS_CACHE_EXPIRY_HOURS, DEFAULT_CACHE_EXPIRY_HOURS
from src.utils.logger import logger

class CacheManager:
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
    
    def _get_cache_key(self, query: str) -> str:
        """Generate a cache key for a query."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get_cached_result(self, query: str) -> str:
        """Get cached result if available and not expired."""
        cache_key = self._get_cache_key(query)
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                cached_time = cached_data.get("timestamp", 0)
                expiry_hours = NEWS_CACHE_EXPIRY_HOURS if "news" in query.lower() else DEFAULT_CACHE_EXPIRY_HOURS
                
                if time.time() - cached_time < expiry_hours * 3600:
                    logger.info(f"Using cached result from {datetime.fromtimestamp(cached_time)}")
                    return cached_data["report"]
            except Exception as e:
                logger.error(f"Error reading cache: {e}")
        
        return None
    
    def cache_result(self, query: str, report: str, duration: float):
        """Cache a research result."""
        cache_key = self._get_cache_key(query)
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    "query": query,
                    "timestamp": time.time(),
                    "duration": duration,
                    "report": report
                }, f)
        except Exception as e:
            logger.error(f"Error caching result: {e}")