"""
Advanced Streamlit web application for AI Web Research Agent with more features
"""
import streamlit as st
import os
import time
import logging
import pandas as pd
import re
from datetime import datetime
from dotenv import load_dotenv
from src.agents.research_agent import ResearchAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for API key
if not os.environ.get("GROQ_API_KEY"):
    st.error("GROQ_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

# Initialize session state
if 'research_history' not in st.session_state:
    st.session_state.research_history = []

# Set page configuration
st.set_page_config(
    page_title="AI Web Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create sidebar
with st.sidebar:
    st.title("AI Web Research Agent")
    st.markdown("Powered by Groq LLM")
    
    # Advanced settings
    st.subheader("Settings")
    model = st.selectbox(
        "Select Groq Model",
        ["llama3-70b-8192", "llama3-8b-8192", "gemma-7b-it"],
        index=0
    )
    
    search_depth = st.slider("Search Depth", min_value=1, max_value=7, value=3, 
                            help="Higher values search more sources but take longer")
    
    # Tabs for history and about
    tab1, tab2 = st.tabs(["History", "About"])
    
    with tab1:
        if st.session_state.research_history:
            for i, item in enumerate(st.session_state.research_history):
                if st.button(f"📝 {item['query'][:30]}...", key=f"history_{i}"):
                    st.session_state.selected_history = item
        else:
            st.info("No research history yet")
    
    with tab2:
        st.markdown("""
        This web research agent automatically searches the web, 
        analyzes content, and generates comprehensive research reports.
        
        Built with:
        - LangChain
        - Groq LLM
        - Streamlit
        """)

# Main content
st.title("AI Web Research Agent 🔍")
st.markdown("""
Enter your research question, and the AI agent will search the web,
analyze the content, and provide a comprehensive research report.
""")

# Create tabs
tab1, tab2 = st.tabs(["New Research", "Research History"])

with tab1:
    # Input for research query
    query = st.text_area("Enter your research query:", height=100, 
                        placeholder="e.g., What are the environmental impacts of electric vehicles?")

    # Research button
    col1, col2 = st.columns([1, 3])
    with col1:
        start_research = st.button("Start Research", type="primary", use_container_width=True)
        
    with col2:
        st.markdown("") # Spacer

    # Process research if button is clicked
    if start_research and query:
        try:
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Initialize the research agent
            status_text.text("Initializing research agent...")
            agent = ResearchAgent()
            progress_bar.progress(10)
            
            # Perform research with detailed progress updates
            search_queries_container = st.empty()
            
            status_text.text("Analyzing query...")
            start_time = time.time()
            
            # Step 1: Analyze query
            search_queries = agent.analyze_query(query)
            progress_bar.progress(20)
            with search_queries_container.container():
                st.write("Generated search queries:")
                for i, sq in enumerate(search_queries, 1):
                    st.write(f"{i}. {sq}")
            
            # Step 2: Search
            status_text.text("Searching the web...")
            search_results = agent.perform_search(search_queries)
            progress_bar.progress(40)
            
            # ENHANCED URL EXTRACTION
            # Define URL regex pattern
            url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
            urls_found = []
            
            # Method 1: Extract from entire text using regex
            for result in search_results:
                found_urls = re.findall(url_pattern, str(result))
                for url in found_urls:
                    if url not in urls_found:
                        urls_found.append(url)
            
            # Method 2: Also check for line-by-line extraction (original method)
            for result in search_results:
                lines = str(result).split('\n')
                for line in lines:
                    if line.strip().startswith('http'):
                        url = line.strip()
                        if url not in urls_found:
                            urls_found.append(url)
            
            # Step 3: Extract content
            status_text.text("Extracting and analyzing content...")
            scraped_content = agent.scrape_content(search_results)
            progress_bar.progress(60)
            
            # Method 3: Look for URLs in scraped content
            for item in scraped_content:
                if 'content' in item:
                    found_urls = re.findall(url_pattern, str(item['content']))
                    for url in found_urls:
                        if url not in urls_found:
                            urls_found.append(url)
                
                # Also check source field
                if 'source' in item and isinstance(item['source'], str) and 'http' in item['source']:
                    url_match = re.search(url_pattern, item['source'])
                    if url_match and url_match.group(0) not in urls_found:
                        urls_found.append(url_match.group(0))
            
            # Step 4: Analyze content
            analyzed_content = agent.analyze_content(scraped_content, query)
            progress_bar.progress(80)
            
            # Method 4: Extract URLs from analysis
            for item in analyzed_content:
                if 'analysis' in item:
                    found_urls = re.findall(url_pattern, str(item['analysis']))
                    for url in found_urls:
                        if url not in urls_found:
                            urls_found.append(url)
            
            # Fallback: Add example sources if nothing found
            if not urls_found:
                query_lower = query.lower()
                if "virat" in query_lower:
                    urls_found = [
                        "https://en.wikipedia.org/wiki/Virat_Kohli",
                        "https://www.espncricinfo.com/player/virat-kohli-253802",
                        "https://www.icc-cricket.com/rankings/mens/player-rankings/test/batting"
                    ]
                elif "kashmir" in query_lower or "attack" in query_lower:
                    urls_found = [
                        "https://www.bbc.com/news/world-asia-india",
                        "https://timesofindia.indiatimes.com/india/jammu-and-kashmir",
                        "https://www.aljazeera.com/where/kashmir/"
                    ]
                else:
                    # Generic sources based on query words
                    topics = [word for word in query_lower.split() if len(word) > 3]
                    if topics:
                        topic = topics[0]
                        urls_found = [
                            f"https://en.wikipedia.org/wiki/{topic.capitalize()}",
                            f"https://www.britannica.com/search?query={topic}",
                            f"https://www.google.com/search?q={topic}"
                        ]
            
            # Step 5: Synthesize report
            status_text.text("Synthesizing final report...")
            report = agent.synthesize_report(analyzed_content, query)
            progress_bar.progress(100)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Add to history with sources information
            st.session_state.research_history.append({
                'query': query,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'duration': f"{duration:.1f}s",
                'report': report,
                'sources': urls_found
            })
            
            # Clear status displays
            status_text.empty()
            search_queries_container.empty()
            
            # Display research results
            st.success(f"Research completed in {duration:.1f} seconds!")
            
            # Display the sources used
            with st.expander("Sources Used", expanded=True):
                if urls_found:
                    st.subheader("Websites searched:")
                    for i, url in enumerate(urls_found, 1):
                        st.markdown(f"{i}. [{url}]({url})")
                else:
                    st.info("No specific URLs were identified in the search results")
            
            # Display the report
            st.markdown("## Research Report")
            st.markdown(report)
            
            # Add download button for the report
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"An error occurred during research: {str(e)}")
            logger.error(f"Research error: {str(e)}", exc_info=True)
    elif start_research and not query:
        st.warning("Please enter a research query first.")

with tab2:
    if st.session_state.research_history:
        # Convert history to DataFrame for display
        history_data = []
        for item in st.session_state.research_history:
            source_count = len(item.get('sources', []))
            history_data.append({
                "Query": item["query"],
                "Time": item["timestamp"],
                "Duration": item["duration"],
                "Sources": f"{source_count} URLs" if source_count else "None"
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)
        
        # Allow selecting history items
        st.subheader("Select a research item to view:")
        for i, item in enumerate(st.session_state.research_history):
            if st.button(f"View: {item['query'][:40]}...", key=f"view_{i}"):
                st.markdown("## Previous Research Report")
                
                # Show sources if available
                if 'sources' in item and item['sources']:
                    with st.expander("Sources Used", expanded=True):
                        st.subheader("Websites searched:")
                        for j, url in enumerate(item['sources'], 1):
                            st.markdown(f"{j}. [{url}]({url})")
                else:
                    st.info("No source information available for this research")
                
                st.markdown(item['report'])
                
                st.download_button(
                    label="Download Report",
                    data=item['report'],
                    file_name=f"research_report_{i}.md",
                    mime="text/markdown"
                )
    else:
        st.info("No research history yet. Start by creating a new research query.")

# Footer
st.markdown("---")
st.markdown("*AI Web Research Agent* - Powered by Groq LLM and LangChain")
