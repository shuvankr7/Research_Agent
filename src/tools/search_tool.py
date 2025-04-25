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
        
        # Query categorization and source mapping
        query_lower = query.strip().lower()
        search_config = self._get_search_config(query_lower)
        
        # Generate targeted search queries
        search_queries = [
            query,  # Original query
            f"{query} {search_config['suffix']}",  # Topic-specific suffix
            f"{query} site:{' OR site:'.join(search_config['primary_sources'])}",  # Primary sources
            f"{query} {search_config['time_filter']}"  # Time relevance
        ]
        
        all_results = []
        for search_query in search_queries:
            payload = {
                'q': search_query,
                'num': max_results,
                'gl': search_config['region']
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

        return self._process_results(all_results, search_config, max_results)

    def _get_search_config(self, query: str) -> Dict:
        """Determine search configuration based on query type."""
        configs = {
            'tech': {
                'primary_sources': ['wikipedia.org', 'github.com', 'stackoverflow.com'],
                'secondary_sources': ['medium.com', 'dev.to', 'towardsdatascience.com'],
                'suffix': 'tutorial guide',
                'time_filter': '',
                'region': 'us'
            },
            'news': {
                'primary_sources': ['reuters.com', 'apnews.com', 'bbc.com'],
                'secondary_sources': ['theguardian.com', 'nytimes.com', 'cnn.com'],
                'suffix': 'latest news',
                'time_filter': 'when:24h',
                'region': 'us'
            },
            'sports': {
                'primary_sources': ['espn.com', 'sports.yahoo.com', 'cricbuzz.com'],
                'secondary_sources': ['ndtv.com/sports', 'timesofindia.com/sports'],
                'suffix': 'latest updates',
                'time_filter': 'when:24h',
                'region': 'in'
            },
            'academic': {
                'primary_sources': ['scholar.google.com', 'researchgate.net', 'arxiv.org'],
                'secondary_sources': ['academia.edu', 'jstor.org'],
                'suffix': 'research paper',
                'time_filter': '',
                'region': 'us'
            },
            'default': {
                'primary_sources': ['wikipedia.org', 'britannica.com'],
                'secondary_sources': ['thoughtco.com', 'howstuffworks.com'],
                'suffix': 'explained guide',
                'time_filter': '',
                'region': 'us'
            }
        }
        
        # Determine query category
        if any(term in query for term in ['programming', 'code', 'software', 'ai', 'machine learning']):
            return configs['tech']
        elif any(term in query for term in ['news', 'latest', 'current', 'today']):
            return configs['news']
        elif any(term in query for term in ['sports', 'cricket', 'football', 'game']):
            return configs['sports']
        elif any(term in query for term in ['research', 'paper', 'study', 'thesis']):
            return configs['academic']
        return configs['default']

    def _process_results(self, results: List[Dict], config: Dict, max_results: int) -> List[Dict]:
        """Process and rank search results."""
        seen_urls = set()
        final_results = []
        
        for item in results:
            link = item.get('link', '')
            if not link or not link.startswith('http'):
                continue
                
            if link not in seen_urls:
                seen_urls.add(link)
                domain = link.split('/')[2].lower()
                
                # Determine result priority
                priority = 3  # Default priority
                if any(source in domain for source in config['primary_sources']):
                    priority = 0
                elif any(source in domain for source in config['secondary_sources']):
                    priority = 1
                
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
