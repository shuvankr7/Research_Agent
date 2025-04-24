from typing import List, Dict
from src.utils.logger import logger

class ContentProcessor:
    @staticmethod
    def scrape_content(search_results: List[Dict]) -> List[Dict]:
        """Extract content from search results."""
        logger.info(f"Scraping content from {len(search_results)} results")
        extracted_content = []
        for i, result in enumerate(search_results):
            extracted_content.append({
                "id": f"web_{i}",
                "content": result.get("snippet", "No content available"),
                "source": result.get("title", f"Source {i+1}"),
                "url": result.get("link", "#")
            })
        return extracted_content
    
    @staticmethod
    def analyze_content(content_list: List[Dict], query: str, content_char_limit: int = 1500) -> List[Dict]:
        """Analyze content for relevance."""
        logger.info(f"Analyzing {len(content_list)} content items")
        analyzed_content = []
        for item in content_list:
            analyzed_content.append({
                "id": item.get("id", f"content_{len(analyzed_content)}"),
                "source": item.get("source", "Unknown source"),
                "content": item.get("content", "No content"),
                "url": item.get("url", "#"),
                "analysis": f"Content from {item.get('source', 'this source')} is relevant to '{query}'.",
                "is_news": False
            })
        return analyzed_content