import os
import sys
import argparse
import logging
import re
import traceback
import hashlib
import json
import time
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.pydantic_v1 import BaseModel, Field
from src.custom_search import CustomSearch

# Import EnhancedSearchTool from test_news_api
# Import the module itself for full access to its functions
import src.test_news_api as search_module
from src.test_news_api import EnhancedSearchTool

# Constants
MAX_RESULTS = 5
DEFAULT_TIMEOUT = 10  # seconds
MIN_DELAY_BETWEEN_REQUESTS = 1.0  # seconds

# Set up logging with console output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

print("Script starting...")

# Load environment variables from .env file
load_dotenv()
print("Environment loaded")

# Check for Groq API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found in environment variables")
    sys.exit(1)
else:
    print("GROQ_API_KEY found")

# Initialize Groq LLM
try:
    print("Initializing Groq LLM...")
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama3-70b-8192",
    )
    print("Groq LLM initialized")
except Exception as e:
    print(f"ERROR initializing Groq LLM: {e}")
    sys.exit(1)

# CRITICAL FIX: ADD THE analyze_query METHOD TO EnhancedSearchTool (don't try to store original)
def analyze_query(self, query):
    """Add analyze_query method to EnhancedSearchTool class."""
    print("Using added analyze_query method")
    processed_query = self.preprocess_query(query)
    return [
        processed_query,
        f"{processed_query} explained", 
        f"{processed_query} definition"
    ]

# Add the method to the class
EnhancedSearchTool.analyze_query = analyze_query
print("Added analyze_query method to EnhancedSearchTool")

class ResearchAgent:
    """Main research agent that orchestrates the research process."""
    
    def __init__(self):
        """Initialize the research agent components."""
        print("Initializing ResearchAgent...")
        self.llm = llm
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.last_request_time = 0
        self.api_key = os.environ.get("SERPER_API_KEY")
        
        # Initialize EnhancedSearchTool directly
        try:
            self.search_tool = EnhancedSearchTool()
            print("EnhancedSearchTool initialized successfully")
        except Exception as e:
            print(f"ERROR initializing EnhancedSearchTool: {e}")
            self.search_tool = None
            sys.exit(1)
        
        print("ResearchAgent initialized")
    
    def _get_cache_key(self, query: str) -> str:
        """Generate a cache key for a query."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def _apply_rate_limiting(self):
        """Apply rate limiting to prevent API throttling."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < MIN_DELAY_BETWEEN_REQUESTS:
            delay = MIN_DELAY_BETWEEN_REQUESTS - elapsed + random.uniform(0.2, 0.8)
            print(f"Rate limiting: Waiting {delay:.2f} seconds")
            time.sleep(delay)
            
        self.last_request_time = time.time()
    
    # ADD THE METHOD THAT'S BEING CALLED BUT IS MISSING
    def analyze_query(self, query: str) -> List[str]:
        """
        Analyze the research query to identify sub-queries and keywords.
        This ensures we have the method if it's called by EnhancedSearchTool.
        """
        print(f"ResearchAgent.analyze_query called with: {query}")
        # Process query to get clean search terms
        processed_query = self.search_tool.preprocess_query(query)
        
        # For simple queries, generate basic search queries
        return [
            processed_query,
            f"{processed_query} information",
            f"{processed_query} explained"
        ]
    
    # ADD THE MISSING PERFORM_SEARCH METHOD
    def perform_search(self, search_queries: List[str], max_results: int = 3) -> List[Dict]:
        """
        Perform search using the provided queries.
        This is called by EnhancedSearchTool.research().
        """
        print(f"ResearchAgent.perform_search called with: {search_queries}")
        results = []
        for query in search_queries:
            try:
                # Use direct_search for each query
                query_results = self.direct_search(query, max_results=max_results)
                results.extend(query_results)
                print(f"Found {len(query_results)} results for query: '{query}'")
            except Exception as e:
                print(f"Error searching for '{query}': {e}")
        
        return results
    
    def direct_search(self, query: str, max_results: int = 3) -> List[Dict]:
        """Direct search implementation using the Serper API."""
        print(f"Direct search for: {query}")
        self._apply_rate_limiting()
        
        api_key = os.environ.get("SERPER_API_KEY")
        if not api_key:
            print("No SERPER_API_KEY found")
            return []
            
        url = "https://google.serper.dev/search"
        payload = {
            'q': query,
            'num': max_results
        }
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'organic' in data and data['organic']:
                for item in data['organic'][:max_results]:
                    title = item.get('title', 'No title')
                    link = item.get('link', '#')
                    snippet = item.get('snippet', 'No description available')
                    
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
            
            return results
        except Exception as e:
            print(f"Direct search error: {e}")
            return []
    
    # ADD OTHER METHODS THAT MIGHT BE MISSING
    def scrape_content(self, search_results: List[Dict]) -> List[Dict]:
        """Extract content from search results."""
        print(f"ResearchAgent.scrape_content called with {len(search_results)} results")
        extracted_content = []
        for i, result in enumerate(search_results):
            extracted_content.append({
                "id": f"web_{i}",
                "content": result.get("snippet", "No content available"),
                "source": result.get("title", f"Source {i+1}"),
                "url": result.get("link", "#")
            })
        return extracted_content
    
    def analyze_content(self, content_list: List[Dict], query: str, content_char_limit: int = 1500) -> List[Dict]:
        """Analyze content for relevance."""
        print(f"ResearchAgent.analyze_content called with {len(content_list)} content items")
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
    
    def synthesize_report(self, analyzed_content: List[Dict], query: str) -> str:
        """Create a report from analyzed content."""
        print(f"ResearchAgent.synthesize_report called with {len(analyzed_content)} content items")
        
        # Format content for LLM
        formatted_content = []
        source_urls = []
        
        for i, item in enumerate(analyzed_content):
            source = item.get("source", f"Source {i+1}")
            content = item.get("content", "No content available")
            url = item.get("url", "#")
            
            formatted_content.append(f"Source {i+1}: {source}\nURL: {url}\nContent: {content}\n")
            source_urls.append(url)
        
        # Generate report using LLM with modified prompt
        prompt = ChatPromptTemplate.from_template(
            """Create a comprehensive research report for the query: {query}
            
            Based on the following information sources:
            
            {content}
            
            INSTRUCTIONS:
            1. Only include factual information from the provided sources
            2. Include citations in square brackets like [1] after statements
            3. Format your response as a well-structured report with markdown headers
            4. For "what is" questions, focus on clear definitions first, then details
            5. Do NOT include separate Resources or References sections at the end
            6. Do NOT label your report with titles like "Research Report" or "Machine Learning Research Report"
            7. Start directly with informative content
            
            Your report should synthesize the information into a cohesive, readable format without unnecessary headers.
            """
        )
        
        chain = prompt | self.llm | StrOutputParser()
        report_content = chain.invoke({
            "query": query,
            "content": "\n\n".join(formatted_content)
        })
        
        # Just list the URLs without extra headers
        sources_urls_text = ""
        for url in source_urls:
            if url != "#":
                sources_urls_text += f"{url}\n"
        
        # Return just the content without extra headers
        return report_content
    
    def research(self, query: str) -> str:
        """
        Perform research on a query.
        """
        query_lower = query.lower().strip()
        print(f"Starting research on: {query}")
        
        # Check cache first
        cache_key = self._get_cache_key(query)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                cached_time = cached_data.get("timestamp", 0)
                # Cache expires after 1 hour for news queries, 24 hours for others
                expiry_hours = 1 if "news" in query_lower else 24
                if time.time() - cached_time < expiry_hours * 3600:
                    print(f"Using cached result from {datetime.fromtimestamp(cached_time).strftime('%Y-%m-%d %H:%M:%S')}")
                    return cached_data["report"]
            except Exception as e:
                print(f"Error reading cache: {e}")
        
        start_time = time.time()
        
        try:
            # OPTION 1: Try to use EnhancedSearchTool directly
            try:
                # This might fail if EnhancedSearchTool tries to call methods on ResearchAgent
                report = self.search_tool.research(query)
                # If successful, return and cache the result
                print("Successfully used EnhancedSearchTool.research directly")
                
                # Store in cache
                duration = time.time() - start_time
                with open(cache_file, 'w') as f:
                    json.dump({
                        "query": query,
                        "timestamp": time.time(),
                        "duration": duration,
                        "report": report
                    }, f)
                
                return report
                
            except AttributeError as e:
                print(f"AttributeError using EnhancedSearchTool: {e}")
                print("Falling back to direct search implementation")
                
                # FALLBACK OPTION: Use direct search implementation
                processed_query = self.search_tool.preprocess_query(query)
                print(f"Processed query: '{processed_query}'")
                
                # Generate search queries
                search_queries = [
                    processed_query,
                    f"{processed_query} definition",
                    f"{processed_query} explained"
                ]
                
                # Perform direct searches
                all_results = []
                for sq in search_queries:
                    results = self.direct_search(sq, max_results=3)
                    all_results.extend(results)
                
                if not all_results:
                    return "No search results found. Please try a different query."
                
                # Format results for report generation
                formatted_results = []
                source_urls = []
                
                for i, result in enumerate(all_results[:5]):
                    formatted_results.append(
                        f"Source {i+1}: {result.get('title', 'No title')}\n"
                        f"URL: {result.get('link', 'No URL')}\n"
                        f"Summary: {result.get('snippet', 'No summary available')}\n"
                    )
                    source_urls.append(result.get('link'))
                
                # Generate report using LLM
                prompt = ChatPromptTemplate.from_template(
                    """Create a comprehensive research report for the query: {query}
                    
                    Based on the following information sources:
                    
                    {content}
                    
                    INSTRUCTIONS:
                    1. Only include factual information from the provided sources
                    2. Include specific citations to websites/sources when possible
                    3. Format your response as a well-structured report with markdown headers
                    4. For "what is" questions, focus on clear definitions first, then details
                    5. Include all relevant URLs from the sources
                    
                    Your report should synthesize the information into a cohesive, readable format.
                    """
                )
                
                chain = prompt | self.llm | StrOutputParser()
                report_content = chain.invoke({
                    "query": query,
                    "content": "\n\n".join(formatted_results)
                })
                
                # Add sources section
                sources_section = "\n\nSources Used\n\nWebsites searched:\n"
                for url in source_urls:
                    sources_section += f"{url}\n"
                
                report = sources_section + "\nResearch Report\n" + report_content
                
                # Store in cache
                duration = time.time() - start_time
                with open(cache_file, 'w') as f:
                    json.dump({
                        "query": query,
                        "timestamp": time.time(),
                        "duration": duration,
                        "report": report
                    }, f)
                
                return report
            
        except Exception as e:
            print(f"Error in research process: {e}")
            traceback.print_exc()
            return f"An error occurred during research: {str(e)}\n\nPlease try again with a different query."

def main():
    """Command line interface for the research agent."""
    print("Entering main function")
    parser = argparse.ArgumentParser(description='AI Web Research Agent')
    parser.add_argument('--query', type=str, help='Research query or question')
    args = parser.parse_args()
    
    try:
        print("Creating ResearchAgent instance...")
        agent = ResearchAgent()
        
        if args.query:
            query = args.query
        else:
            print("\nAI Web Research Agent 🔍")
            print("Enter your research question, and the AI agent will search the web, analyze the content, and provide a comprehensive research report.")
            print("\nNew Research\n")
            print("Research History\n")
            query = input("Enter your research query:\n")
        
        start_time = time.time()
        report = agent.research(query)
        end_time = time.time()
        
        print(f"Research completed in {end_time - start_time:.1f} seconds!")
        print(f"\n{report}")
        print("\nAI Web Research Agent - Powered by Groq LLM and LangChain")
    except Exception as e:
        print(f"ERROR in main function: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Script called directly")
    main()
else:
    print("Script imported as module")