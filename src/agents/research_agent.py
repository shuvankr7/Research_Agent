import time
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.utils.config import GROQ_API_KEY, DEFAULT_MODEL
from src.utils.logger import logger
from src.tools.search_tool import SearchTool
from src.tools.content_processor import ContentProcessor
from src.tools.cache_manager import CacheManager

class ResearchAgent:
    def __init__(self):
        """Initialize the research agent components."""
        logger.info("Initializing ResearchAgent...")
        
        # Initialize LLM
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=DEFAULT_MODEL,
        )
        
        # Initialize components
        self.search_tool = SearchTool()
        self.content_processor = ContentProcessor()
        self.cache_manager = CacheManager()
        
        logger.info("ResearchAgent initialized")
    
    def analyze_query(self, query: str) -> List[str]:
        """Enhance query analysis to better understand intent."""
        prompt = ChatPromptTemplate.from_template(
            """Analyze this research query: {query}
            Generate 3-5 search queries that will help find:
            1. Core factual information
            2. Recent developments/news
            3. Different perspectives/analyses
            Return only the queries, one per line."""
        )
        
        chain = prompt | self.llm | StrOutputParser()
        expanded_queries = chain.invoke({"query": query}).split('\n')
        return [q.strip() for q in expanded_queries if q.strip()]
    
    def synthesize_report(self, analyzed_content: List[Dict], query: str) -> str:
        """Create a report from analyzed content."""
        logger.info(f"Synthesizing report from {len(analyzed_content)} content items")
        
        formatted_content = []
        for item in analyzed_content:
            # Extract domain name and clean it
            url = item.get('url', '')
            domain = url.split('//')[1].split('/')[0] if '//' in url else url
            source_name = domain.replace('www.', '').split('.')[0].upper()
            
            formatted_content.append(
                f"Source: {source_name}\n"
                f"URL: {url}\n"
                f"Content: {item.get('content')}\n"
            )
        
        prompt = ChatPromptTemplate.from_template(
            """Create a comprehensive research report for the query: {query}
            
            Based on the following information sources:
            
            {content}
            
            INSTRUCTIONS:
            1. Use the source website names for citations (e.g., [CRICINFO], [NDTV])
            2. Each fact should be followed by the source citation
            3. Format your response as a well-structured report with markdown headers
            4. Only include factual information from the provided sources
            5. Do NOT include separate References or Sources sections
            6. Avoid using numerical citations like [1], [2], etc.
            
            Your report should synthesize the information into a cohesive, readable format.
            """
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "query": query,
            "content": "\n\n".join(formatted_content)
        })
    
    def research(self, query: str) -> str:
        """Perform research on a query."""
        logger.info(f"Starting research on: {query}")
        
        # Check cache first
        cached_result = self.cache_manager.get_cached_result(query)
        if cached_result:
            return cached_result
        
        start_time = time.time()
        
        try:
            # Generate search queries
            search_queries = self.analyze_query(query)
            
            # Perform searches
            all_results = []
            for sq in search_queries:
                results = self.search_tool.direct_search(sq, max_results=3)
                all_results.extend(results)
            
            if not all_results:
                return "No search results found. Please try a different query."
            
            # Process content
            scraped_content = self.content_processor.scrape_content(all_results)
            analyzed_content = self.content_processor.analyze_content(scraped_content, query)
            
            # Generate report
            report = self.synthesize_report(analyzed_content, query)
            
            # Cache result
            duration = time.time() - start_time
            self.cache_manager.cache_result(query, report, duration)
            
            return report
            
        except Exception as e:
            logger.error(f"Error in research process: {e}", exc_info=True)
            return f"An error occurred during research: {str(e)}\n\nPlease try again with a different query."

    def perform_search(self, search_queries: List[str], max_results: int = 3) -> List[Dict]:
        """Perform search using the provided queries."""
        logger.info(f"Performing search with queries: {search_queries}")
        results = []
        for query in search_queries:
            search_results = self.search_tool.direct_search(query, max_results=max_results)
            results.extend(search_results)
        return results
    
    # Add these methods from the content processor to make them accessible through ResearchAgent
    def scrape_content(self, search_results: List[Dict]) -> List[Dict]:
        """Proxy method to content processor's scrape_content."""
        return self.content_processor.scrape_content(search_results)
    
    def analyze_content(self, content_list: List[Dict], query: str) -> List[Dict]:
        """Proxy method to content processor's analyze_content."""
        return self.content_processor.analyze_content(content_list, query)