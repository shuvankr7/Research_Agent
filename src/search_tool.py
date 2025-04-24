"""
Search tool module for performing web searches to find relevant information.
"""
import os
import logging
import json
from typing import List, Dict, Any
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class SearchTool:
    """
    Tool for performing web searches using various search engines.
    """
    
    def __init__(self):
        """Initialize the search tool with API keys."""
        self.serper_api_key = os.environ.get("SERPER_API_KEY", "")
        self.serpapi_api_key = os.environ.get("SERPAPI_API_KEY", "")
        
        if not self.serper_api_key and not self.serpapi_api_key:
            logger.warning("No search API keys provided. Search functionality will be limited.")
    
    def search_serper(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search using Serper.dev API.
        
        Args:
            query: Search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        if not self.serper_api_key:
            logger.warning("Serper API key not found")
            return []
            
        url = "https://serpapi.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "num": num_results
        })
        
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "organic" in data:
                for item in data["organic"][:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "serper"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Serper search error: {str(e)}")
            return []
    
    def search_serpapi(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search using SerpAPI.
        
        Args:
            query: Search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        if not self.serpapi_api_key:
            logger.warning("SerpAPI key not found")
            return []
            
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": self.serpapi_api_key,
            "num": num_results
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "organic_results" in data:
                for item in data["organic_results"][:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "serpapi"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"SerpAPI search error: {str(e)}")
            return []
    
    def duckduckgo_search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fallback search using DuckDuckGo (no API key needed).
        
        Args:
            query: Search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        try:
            # This is a simplified implementation that would need to be enhanced
            # with proper HTML parsing in a real application
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Note: This is a simplification - in reality you would parse the HTML properly
            # to extract search results. Here we're just returning a placeholder.
            logger.warning("DuckDuckGo search would require HTML parsing - returning placeholder")
            return [{
                "title": f"Result for {query}",
                "url": f"https://duckduckgo.com/?q={quote_plus(query)}",
                "snippet": "Please implement proper HTML parsing for DuckDuckGo results",
                "source": "duckduckgo"
            }]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    def search(self, queries: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform search using multiple search engines and queries.
        
        Args:
            queries: List of search queries
            max_results: Maximum total results to return
            
        Returns:
            List of search results
        """
        logger.info(f"Performing search with {len(queries)} queries")
        
        all_results = []
        results_per_query = max(1, max_results // len(queries))
        
        for query in queries:
            # Try Serper first
            results = self.search_serper(query, results_per_query)
            
            # If no results, try SerpAPI
            if not results and self.serpapi_api_key:
                results = self.search_serpapi(query, results_per_query)
            
            # If still no results, fall back to DuckDuckGo
            if not results:
                results = self.duckduckgo_search(query, results_per_query)
            
            all_results.extend(results)
            
            # Stop if we have enough results
            if len(all_results) >= max_results:
                break
                
        # Deduplicate results by URL
        unique_results = []
        seen_urls = set()
        for result in all_results:
            if result["url"] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result["url"])
                
                # Stop if we have enough unique results
                if len(unique_results) >= max_results:
                    break
        
        logger.info(f"Search complete: {len(unique_results)} unique results found")
        return unique_results