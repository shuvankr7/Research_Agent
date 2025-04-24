"""
Query analyzer module for understanding and expanding research queries.
"""
import logging
from typing import Dict, List, Any
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

class QueryAnalyzer:
    """
    Analyzes research queries to extract keywords, generate search queries,
    and identify the type of information needed.
    """
    
    def __init__(self):
        """Initialize the query analyzer with required NLTK data."""
        try:
            # Download necessary NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            logger.warning(f"Could not download NLTK data: {str(e)}")
            self.stop_words = set()
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract important keywords from the query.
        
        Args:
            query: The research query
            
        Returns:
            List of keywords
        """
        # Tokenize and remove stop words
        word_tokens = word_tokenize(query.lower())
        keywords = [word for word in word_tokens if word.isalnum() and word not in self.stop_words]
        
        # Identify keyphrases (adjacent keywords)
        keyphrases = []
        for i in range(len(word_tokens) - 1):
            if (word_tokens[i] not in self.stop_words and 
                word_tokens[i+1] not in self.stop_words and
                word_tokens[i].isalnum() and 
                word_tokens[i+1].isalnum()):
                keyphrases.append(f"{word_tokens[i]} {word_tokens[i+1]}")
        
        # Combine unique keywords and keyphrases
        all_keys = list(set(keywords + keyphrases))
        
        # Sort by length (longer is usually more specific)
        all_keys.sort(key=len, reverse=True)
        
        # Take top 10 or fewer
        return all_keys[:10]
    
    def generate_search_queries(self, keywords: List[str], original_query: str) -> List[str]:
        """
        Generate search queries from keywords and original query.
        
        Args:
            keywords: List of extracted keywords
            original_query: Original research query
            
        Returns:
            List of search queries
        """
        queries = [original_query]  # Always include original query
        
        # Generate 2-3 alternative queries
        if len(keywords) >= 3:
            queries.append(' '.join(keywords[:3]))
        
        if len(keywords) >= 5:
            queries.append(' '.join(keywords[1:4]))
        
        # Add a "what is" query if the query seems definitional
        if not any(q.lower().startswith("what is") or q.lower().startswith("define") for q in queries):
            if len(keywords) > 1:
                queries.append(f"what is {' '.join(keywords[:2])}")
        
        return list(set(queries))
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query and extract useful information.
        
        Args:
            query: The research query
            
        Returns:
            Dict containing analysis results
        """
        logger.info(f"Analyzing query: {query}")
        
        # Extract keywords
        keywords = self.extract_keywords(query)
        logger.debug(f"Extracted keywords: {keywords}")
        
        # Generate search queries
        search_queries = self.generate_search_queries(keywords, query)
        logger.debug(f"Generated search queries: {search_queries}")
        
        # Determine the research category based on query structure
        query_lower = query.lower()
        category = "factual"  # default
        
        if any(word in query_lower for word in ["how to", "steps", "guide", "tutorial"]):
            category = "instructional"
        elif any(word in query_lower for word in ["compare", "versus", "vs", "difference"]):
            category = "comparison"
        elif any(word in query_lower for word in ["why", "reason", "cause"]):
            category = "explanatory"
        elif any(word in query_lower for word in ["best", "top", "review", "recommend"]):
            category = "evaluative"
        
        return {
            "original_query": query,
            "keywords": keywords,
            "search_queries": search_queries,
            "category": category
        }