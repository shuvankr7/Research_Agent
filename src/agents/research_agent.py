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
            Generate 5-7 search queries that will help find:
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
            6. Avoid using numerical citations like [1], [2],[3,7,8] etc.
            
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
        
        if not search_queries or not any(query.strip() for query in search_queries):
            raise ValueError("Search queries cannot be empty")
            
        results = []
        for query in search_queries:
            if query.strip():  # Only search non-empty queries
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
    
    def generate_research_report(self, query: str, search_results: List[Dict]) -> str:
        """Generate comprehensive research report with in-depth analysis."""
        
        # Organize content by themes
        themes = self._categorize_content(search_results)
        
        # Generate report sections
        sections = {
            'introduction': self._generate_introduction(query, themes),
            'background': self._generate_background(themes),
            'main_findings': self._generate_main_findings(themes),
            'analysis': self._generate_analysis(themes),
            'implications': self._generate_implications(themes),
            'future_outlook': self._generate_future_outlook(themes),
            'expert_opinions': self._generate_expert_opinions(themes),
            'challenges': self._generate_challenges(themes),
            'recommendations': self._generate_recommendations(themes),
            'conclusion': self._generate_conclusion(themes)
        }
        
        # Compile report
        report = f"""# Comprehensive Research Report: {query}
    
        ## Executive Summary
        {sections['introduction']}
    
        ## Background and Context
        {sections['background']}
    
        ## Key Findings
        {sections['main_findings']}
    
        ## Detailed Analysis
        {sections['analysis']}
    
        ## Industry Implications
        {sections['implications']}
    
        ## Expert Insights and Opinions
        {sections['expert_opinions']}
    
        ## Challenges and Limitations
        {sections['challenges']}
    
        ## Future Outlook
        {sections['future_outlook']}
    
        ## Recommendations
        {sections['recommendations']}
    
        ## Conclusion
        {sections['conclusion']}
    
        ## Sources
        {self._generate_sources(search_results)}
        """
        return report
    
    def _categorize_content(self, results: List[Dict]) -> Dict:
        """Categorize content into themes for better organization."""
        themes = {
            'overview': [],
            'technical': [],
            'market': [],
            'challenges': [],
            'future': [],
            'expert_views': [],
            'statistics': [],
            'case_studies': [],
            'regulations': [],
            'innovations': []
        }
        
        for result in results:
            # Categorize based on content analysis
            content = result.get('snippet', '').lower()
            
            if any(word in content for word in ['market', 'industry', 'economy']):
                themes['market'].append(result)
            if any(word in content for word in ['challenge', 'problem', 'issue']):
                themes['challenges'].append(result)
            if any(word in content for word in ['future', 'prediction', 'forecast']):
                themes['future'].append(result)
            if any(word in content for word in ['expert', 'analyst', 'specialist']):
                themes['expert_views'].append(result)
            if any(word in content for word in ['innovation', 'development', 'breakthrough']):
                themes['innovations'].append(result)
                
        return themes
    
    def _generate_analysis(self, themes: Dict) -> str:
        """Generate detailed analysis section with supporting evidence."""
        analysis = []
        
        # Market Analysis
        if themes['market']:
            analysis.append("### Market Analysis")
            analysis.append(self._analyze_market_trends(themes['market']))
        
        # Technical Analysis
        if themes['technical']:
            analysis.append("### Technical Developments")
            analysis.append(self._analyze_technical_aspects(themes['technical']))
        
        # Impact Analysis
        if themes['implications']:
            analysis.append("### Impact Assessment")
            analysis.append(self._analyze_implications(themes['implications']))
        
        # Statistical Analysis
        if themes['statistics']:
            analysis.append("### Statistical Insights")
            analysis.append(self._analyze_statistics(themes['statistics']))
        
        return "\n\n".join(analysis)
    
    def _generate_expert_opinions(self, themes: Dict) -> str:
        """Generate expert opinions section with diverse viewpoints."""
        opinions = []
        
        if themes['expert_views']:
            for view in themes['expert_views']:
                expert_name = self._extract_expert_name(view)
                if expert_name:
                    opinions.append(f"**{expert_name}** suggests: {view['snippet']}")
                else:
                    opinions.append(f"Industry experts note: {view['snippet']}")
        
        return "\n\n".join(opinions) if opinions else "Expert opinions not available in the current sources."
    
    def _generate_recommendations(self, themes: Dict) -> str:
        """Generate actionable recommendations based on research."""
        recommendations = []
        
        # Short-term recommendations
        recommendations.append("### Short-term Actions")
        recommendations.extend(self._generate_short_term_recommendations(themes))
        
        # Long-term strategies
        recommendations.append("### Long-term Strategies")
        recommendations.extend(self._generate_long_term_recommendations(themes))
        
        # Risk mitigation
        recommendations.append("### Risk Mitigation")
        recommendations.extend(self._generate_risk_recommendations(themes))
        
        return "\n\n".join(recommendations)
