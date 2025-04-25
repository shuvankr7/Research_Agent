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
        
        # Enhanced query processing for better relevance
        base_query = query.strip()
        search_queries = [
            base_query,  # Original query
            f"{base_query} latest news",  # Latest news
            f"{base_query} site:cricbuzz.com OR site:espncricinfo.com OR site:bcci.tv",  # Sports specific
            f"{base_query} last 24 hours"  # Recent content
        ]
        
        all_results = []
        for search_query in search_queries:
            payload = {
                'q': search_query,
                'num': max_results,
                'tbs': 'qdr:d',  # Last 24 hours
                'gl': 'in'  # Prioritize Indian results for cricket
            }
            
            try:
                response = requests.post(url, 
                    headers={'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'},
                    json=payload, 
                    timeout=DEFAULT_TIMEOUT
                )
                response.raise_for_status()
                data = response.json()
                
                if 'organic' in data:
                    all_results.extend(data['organic'])
                    
            except Exception as e:
                logger.error(f"Search error for query '{search_query}': {e}")
                continue
        
        # Deduplicate and rank results
        seen_urls = set()
        final_results = []
        
        for item in all_results:
            link = item.get('link', '')
            if not link or not link.startswith('http'):
                continue
                
            if link not in seen_urls:
                seen_urls.add(link)
                domain = link.split('/')[2].lower()
                
                # Prioritize trusted sources
                priority = 1
                if any(site in domain for site in ['cricbuzz.com', 'espncricinfo.com', 'bcci.tv']):
                    priority = 0
                elif any(site in domain for site in ['ndtv.com', 'timesofindia.com', 'hindustantimes.com']):
                    priority = 2
                
                final_results.append({
                    'title': item.get('title', 'No title'),
                    'link': link,
                    'snippet': item.get('snippet', 'No description available'),
                    'time': item.get('date', 'Recent'),
                    'priority': priority
                })
        
        # Sort by priority and return top results
        final_results.sort(key=lambda x: x['priority'])
        return final_results[:max_results]
