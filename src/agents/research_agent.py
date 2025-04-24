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
        """Analyze and expand the research query."""
        logger.info(f"Analyzing query: {query}")
        return [
            query,
            f"{query} information",
            f"{query} explained"
        ]
    
    def synthesize_report(self, analyzed_content: List[Dict], query: str) -> str:
        """Create a report from analyzed content."""
        logger.info(f"Synthesizing report from {len(analyzed_content)} content items")
        
        formatted_content = []
        for i, item in enumerate(analyzed_content):
            source_name = item.get('source', '').split('.')[0].title()  # Extract website name
            formatted_content.append(
                f"Source: {source_name}\n"
                f"URL: {item.get('url')}\n"
                f"Content: {item.get('content')}\n"
            )
        
        prompt = ChatPromptTemplate.from_template(
            """Create a comprehensive research report for the query: {query}
            
            Based on the following information sources:
            
            {content}
            
            INSTRUCTIONS:
            1. Use source names for citations (e.g., [ESPNCricinfo], [NDTVSports]) instead of numbers
            2. Format your response as a well-structured report with markdown headers
            3. Only include factual information from the provided sources
            4. For "what is" questions, focus on clear definitions first, then details
            5. Do NOT include separate Resources or References sections
            6. Cite sources using the website name in square brackets
            
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