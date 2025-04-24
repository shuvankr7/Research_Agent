AI Web Research Agent with Groq LLM

# Project Overview

An advanced Python-based AI agent that performs comprehensive web research automatically with minimal human input. The agent:

Analyzes user research queries and identifies intent
Searches the web using multiple search engine APIs with fallbacks
Extracts, scrapes, and processes content from web pages
Analyzes content relevance and extracts key information
Generates well-structured research reports with proper citations
Handles errors gracefully with multiple fallback mechanisms

# Technologies & Tools Implemented

* Language Models: Groq LLM (Llama-3-70B) for advanced text processing and report generation

* Search Engines:

Serper API (Google Search results)
Custom fallbacks for when APIs fail
Domain-specific optimized search

* Content Processing:

BeautifulSoup & Trafilatura for robust web scraping
NLTK for content analysis and keyword extraction
Rate limiting to respect website terms

* Frameworks:

LangChain for orchestration and prompt management
Streamlit for interactive web interface
Pydantic models for structured data handling

* Support Systems:

Intelligent caching mechanism for rapid responses
Comprehensive logging system
Error handling with graceful degradation

# Module Structure

main.py – Core research agent with orchestration logic
query_analyzer.py – Intelligent query analysis with keyword extraction
search_tool.py – Multi-source search with fallbacks
custom_search.py – Enhanced search with domain-specific optimization
test_news_api.py – Reliable search implementation with Serper API
scraper.py – Content extraction with BeautifulSoup & Trafilatura
content_analyzer.py – Content relevance analysis and key sentence extraction
synthesizer.py – Report generation with topic organization
models.py – Data models for structured information flow
app.py – web interface 

# Key Features

* Advanced Query Processing:

Question transformation (e.g., "What is X?" → "X definition")
Keyword extraction for optimal search
Query intent classification

* Robust Search Capabilities:

Multi-query search strategy
API fallbacks when primary search fails
Domain-specific search optimization
Rate limiting to prevent API blocks

* Content Extraction & Analysis:

Intelligent relevance scoring
Key sentence identification
Source credibility assessment
Structured data extraction

* Smart Report Generation:

Information synthesis across sources
Topic-based organization
Proper citation and attribution
Formatted markdown output

* Practical Enhancements:

Result caching for performance
Comprehensive error handling
Progress reporting
Clean web interface
Report download functionality

# Configuration & Setup
Environment Variables
Create a .env file with the following variables:

GROQ_API_KEY="your_groq_api_key"
SERPER_API_KEY="your_serper_api_key"
NEWS_API_KEY="your_news_api_key"
USER_AGENT="your_custom_user_agent"
LOG_LEVEL=INFO
MAX_SEARCH_RESULTS=5
MAX_CONTENT_LENGTH=50000
REQUEST_TIMEOUT=30


Installation

# Clone the repository

git clone https://github.com/shuvankar7/ai-web-research-agent.git
cd ai-web-research-agent

# Install dependencies

pip install -r requirements.txt

# Run the command-line interface

python -m src.main

# Run the web interface

streamlit run app.py


# Usage Examples
* Command Line

python -m src.main --query "Your Question"



# Web Interface

Run streamlit run app.py
Enter your research query in the text box
Click "Start Research"
View the generated report and download as Markdown


#  Testing Scenarios

The research agent has been tested with:

* Simple factual queries ("What is machine learning?")
* Comparative analyses ("Compare Python vs JavaScript")
* Current events research ("Latest developments in renewable energy")
* Domain-specific research (technical, scientific, and general topics)
* Error cases (API failures, content extraction issues)


# Implementation Details

Research Process Flow
Query analysis and preprocessing
Generation of optimal search queries
Web search with multiple fallback mechanisms
Content extraction from search results
Relevance analysis and information ranking
Report synthesis using Groq LLM
Result caching and presentation
Error Handling
Multiple fallbacks for search APIs
Graceful degradation when services are unavailable
Informative error messages
Default content for common research topics

# Future Enhancements

Full webpage scraping beyond search snippets
More sophisticated news aggregation integration
Improved structured data extraction (tables, lists)
Enhanced conflict resolution between contradictory sources
Additional search engine integrations

# License

This project is licensed under the MIT License - see the LICENSE file for details.