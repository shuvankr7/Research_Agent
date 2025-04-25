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
        
        # Improve search query for sports/cricket related queries
        if any(keyword in query.lower() for keyword in ['ipl', 'cricket', 'match', 'score']):
            query = f"{query} site:cricbuzz.com OR site:espncricinfo.com OR site:bcci.tv"
        
        payload = {
            'q': query,
            'num': max_results * 2,  # Request more results to filter
            'tbs': 'qdr:d'  # Restrict to last 24 hours for recent content
        }
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
                for item in data['organic']:
                    # Prioritize trusted sports websites
                    link = item.get('link', '')
                    if link and link.startswith('http'):
                        # Filter and prioritize reliable sources
                        domain = link.split('/')[2].lower()
                        if (any(site in domain for site in ['cricbuzz.com', 'espncricinfo.com', 'bcci.tv']) or
                            len(results) < max_results):
                            results.append({
                                'title': item.get('title', 'No title'),
                                'link': link,
                                'snippet': item.get('snippet', 'No description available'),
                                'time': item.get('date', 'Recent')
                            })
                            if len(results) >= max_results:
                                break
            return results
            
        except Exception as e:
            logger.error(f"Direct search error: {e}")
            return []
