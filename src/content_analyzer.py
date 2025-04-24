"""
Content analyzer module for processing and analyzing web page content.
"""
import logging
from typing import List, Dict, Any
import re
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """
    Analyzes web content for relevance, extracts key information,
    and structures content for synthesis.
    """
    
    def __init__(self):
        """Initialize the content analyzer with necessary resources."""
        try:
            # Download necessary NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            logger.warning(f"Could not download NLTK data: {str(e)}")
            self.stop_words = set()
    
    def calculate_relevance_score(self, content: str, query_analysis: Dict[str, Any]) -> float:
        """
        Calculate relevance score of content to the query.
        
        Args:
            content: Text content to analyze
            query_analysis: Query analysis dict from QueryAnalyzer
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        content_lower = content.lower()
        keywords = query_analysis['keywords']
        
        # Count keyword occurrences
        keyword_count = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_count += content_lower.count(keyword_lower)
        
        # Normalize by content length and number of keywords
        content_words = len(content_lower.split())
        if content_words == 0 or len(keywords) == 0:
            return 0.0
            
        normalized_count = keyword_count / (content_words * len(keywords))
        
        # Calculate presence ratio (what portion of keywords appear in the content)
        keywords_present = sum(1 for keyword in keywords if keyword.lower() in content_lower)
        presence_ratio = keywords_present / len(keywords)
        
        # Combine factors
        relevance_score = 0.4 * normalized_count + 0.6 * presence_ratio
        
        # Cap at 1.0
        return min(relevance_score, 1.0)
    
    def extract_key_sentences(self, content: str, query_analysis: Dict[str, Any], max_sentences: int = 10) -> List[str]:
        """
        Extract key sentences that are most relevant to the query.
        
        Args:
            content: Text content to analyze
            query_analysis: Query analysis dict from QueryAnalyzer
            max_sentences: Maximum number of sentences to extract
            
        Returns:
            List of key sentences
        """
        # Split into sentences
        sentences = sent_tokenize(content)
        if not sentences:
            return []
            
        # Score each sentence by keyword presence
        keywords = set(keyword.lower() for keyword in query_analysis['keywords'])
        sentence_scores = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Count keywords in sentence
            keyword_matches = sum(keyword in sentence_lower for keyword in keywords)
            
            # Calculate score based on keyword density
            score = keyword_matches / max(1, len(sentence.split()))
            
            # Boost score for sentences that contain multiple keywords
            if keyword_matches > 1:
                score *= 1.5
                
            sentence_scores.append((sentence, score))
        
        # Sort by score and take top sentences
        top_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:max_sentences]
        
        # Sort sentences by their original order for better readability
        original_order = [(i, sentence) for i, (sentence, _) in enumerate(top_sentences)]
        original_order.sort(key=lambda x: sentences.index(x[1]))
        
        return [sentence for _, sentence in original_order]
    
    def extract_metadata(self, content_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract additional metadata from content.
        
        Args:
            content_dict: Dictionary with content and metadata
            
        Returns:
            Dict with extracted metadata
        """
        content = content_dict['content']
        
        # Extract potential date patterns
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, content))
        
        # Extract most common words (excluding stopwords)
        words = word_tokenize(content.lower())
        filtered_words = [word for word in words 
                         if word.isalnum() and 
                         word not in self.stop_words and
                         len(word) > 2]
        
        word_freq = Counter(filtered_words)
        common_words = [word for word, count in word_freq.most_common(10)]
        
        # Estimate reading time
        word_count = len(content.split())
        reading_time_mins = max(1, word_count // 200)  # Assume 200 words per minute
        
        return {
            'dates_mentioned': dates[:5],  # Limit to 5 dates
            'common_terms': common_words,
            'word_count': word_count,
            'reading_time_mins': reading_time_mins
        }
    
    def analyze(self, scraped_contents: List[Dict[str, Any]], 
               query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze scraped content and extract relevant information.
        
        Args:
            scraped_contents: List of scraped content dictionaries
            query_analysis: Query analysis dict from QueryAnalyzer
            
        Returns:
            List of analyzed content with relevance scores and key points
        """
        logger.info(f"Analyzing {len(scraped_contents)} scraped documents")
        
        analyzed_results = []
        
        for content_dict in scraped_contents:
            try:
                content = content_dict['content']
                
                # Skip very short content
                if len(content.split()) < 50:
                    logger.debug(f"Skipping short content from {content_dict['url']}")
                    continue
                
                # Calculate relevance score
                relevance = self.calculate_relevance_score(content, query_analysis)
                
                # Skip irrelevant content
                if relevance < 0.1:  # Threshold can be adjusted
                    logger.debug(f"Skipping irrelevant content from {content_dict['url']}")
                    continue
                
                # Extract key sentences
                key_sentences = self.extract_key_sentences(content, query_analysis)
                
                # Extract metadata
                metadata = self.extract_metadata(content_dict)
                
                analyzed_results.append({
                    'url': content_dict['url'],
                    'title': content_dict['title'],
                    'relevance_score': relevance,
                    'key_sentences': key_sentences,
                    'metadata': metadata,
                    'content': content  # Include full content for synthesizer
                })
                
            except Exception as e:
                logger.error(f"Error analyzing content from {content_dict['url']}: {str(e)}")
        
        # Sort by relevance score
        analyzed_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"Content analysis complete: {len(analyzed_results)} relevant documents found")
        return analyzed_results