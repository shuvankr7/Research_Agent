import requests
import time
import random
from typing import List, Dict
from src.utils.config import SERPER_API_KEY, DEFAULT_TIMEOUT, MIN_DELAY_BETWEEN_REQUESTS
from src.utils.logger import logger

class SearchTool:
    def __init__(self):
        self.last_request_time = 0
        
    def _apply_rate_limiting(self):
        """Apply rate limiting to prevent API throttling."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < MIN_DELAY_BETWEEN_REQUESTS:
            delay = MIN_DELAY_BETWEEN_REQUESTS - elapsed + random.uniform(0.2, 0.8)
            logger.info(f"Rate limiting: Waiting {delay:.2f} seconds")
            time.sleep(delay)
            
        self.last_request_time = time.time()
    
    def direct_search(self, query: str, max_results: int = 3) -> List[Dict]:
        """Direct search implementation using the Serper API."""
        logger.info(f"Direct search for: {query}")
        self._apply_rate_limiting()
        
        if not SERPER_API_KEY:
            logger.warning("No SERPER_API_KEY found")
            return []
            
        url = "https://google.serper.dev/search"
        payload = {'q': query, 'num': max_results}
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'organic' in data and data['organic']:
                for item in data['organic'][:max_results]:
                    results.append({
                        'title': item.get('title', 'No title'),
                        'link': item.get('link', '#'),
                        'snippet': item.get('snippet', 'No description available')
                    })
            return results
            
        except Exception as e:
            logger.error(f"Direct search error: {e}")
            return []