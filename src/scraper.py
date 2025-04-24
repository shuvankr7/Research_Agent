"""
Web scraper module for extracting content from web pages.
"""
import logging
import requests
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import trafilatura
import time
import random

logger = logging.getLogger(__name__)

class Scraper:
    """
    Web scraper for extracting content from web pages.
    """
    
    def __init__(self):
        """Initialize the scraper with default settings."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        self.timeout = 10
        self.rate_limit = (1, 3)  # Random delay between 1-3 seconds
    
    def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a web page.
        
        Args:
            url: URL of the web page to scrape
            
        Returns:
            Dict containing the scraped content or None if failed
        """
        logger.info(f"Scraping: {url}")
        
        # Add rate limiting
        time.sleep(random.uniform(*self.rate_limit))
        
        try:
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            html = response.text
            
            # Try trafilatura first for content extraction
            extracted_text = trafilatura.extract(html, include_comments=False, include_tables=True)
            
            # If trafilatura fails, fall back to BeautifulSoup
            if not extracted_text:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text
                extracted_text = soup.get_text(separator='\n', strip=True)
            
            # Extract title
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else ''
            
            # Extract metadata
            meta_description = ''
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_description = meta_tag.get('content', '')
            
            # Clean and normalize text
            if extracted_text:
                # Remove excessive whitespace
                import re
                extracted_text = re.sub(r'\n+', '\n', extracted_text)
                extracted_text = re.sub(r' +', ' ', extracted_text)
                
                logger.info(f"Successfully scraped {url} ({len(extracted_text)} chars)")
                return {
                    'url': url,
                    'title': title,
                    'meta_description': meta_description,
                    'content': extracted_text,
                    'html': html  # Include raw HTML for advanced processing if needed
                }
            else:
                logger.warning(f"Failed to extract content from {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def extract_article_text(self, html_content: str) -> str:
        """
        Extract main article text from HTML content.
        
        Args:
            html_content: HTML content of the web page
            
        Returns:
            Extracted article text
        """
        return trafilatura.extract(html_content, include_comments=False, include_tables=True) or ""
    
    def extract_links(self, html_content: str, base_url: str) -> list:
        """
        Extract links from HTML content.
        
        Args:
            html_content: HTML content of the web page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of extracted links
        """
        from urllib.parse import urljoin
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            if link.startswith('http'):  # Skip non-HTTP links
                links.append({
                    'url': link,
                    'text': a_tag.get_text(strip=True)
                })
        
        return links