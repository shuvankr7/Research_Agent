"""
Synthesizer module for creating a cohesive research report.
"""
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class Synthesizer:
    """
    Synthesizes analyzed content into coherent research findings.
    """
    
    def __init__(self):
        """Initialize the synthesizer."""
        pass
    
    def _organize_by_topic(self, analyzed_contents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Organize key sentences by topic clusters.
        
        Args:
            analyzed_contents: List of analyzed content
            
        Returns:
            Dict of topics with associated sentences
        """
        # Extract all key sentences
        all_sentences = []
        for content in analyzed_contents:
            all_sentences.extend([{
                'text': sentence, 
                'source': content['title'],
                'url': content['url'],
                'relevance': content['relevance_score']
            } for sentence in content['key_sentences']])
        
        # For a simple implementation, we'll group by common terms
        # In a real application, we might use clustering or topic modeling
        topics = {}
        common_terms = set()
        
        for content in analyzed_contents:
            if 'metadata' in content and 'common_terms' in content['metadata']:
                common_terms.update(content['metadata']['common_terms'])
        
        # Use top common terms as topic labels
        top_terms = list(common_terms)[:8]  # Limit to 8 topics
        
        for term in top_terms:
            term_sentences = [
                sent for sent in all_sentences 
                if term in sent['text'].lower()
            ]
            if term_sentences:
                topics[term] = term_sentences
        
        # Add "Other" category for sentences not matched
        matched_sentences = set()
        for term, sentences in topics.items():
            matched_sentences.update([s['text'] for s in sentences])
            
        other_sentences = [
            sent for sent in all_sentences 
            if sent['text'] not in matched_sentences
        ]
        
        if other_sentences:
            topics['other'] = other_sentences
            
        return topics
    
    def _create_summary(self, query: str, topics: Dict[str, List[Dict[str, str]]], 
                       analyzed_contents: List[Dict[str, Any]]) -> str:
        """
        Create a cohesive summary from organized topics.
        
        Args:
            query: Original research query
            topics: Dict of topics with associated sentences
            analyzed_contents: List of analyzed content
            
        Returns:
            Research summary text
        """
        summary_parts = [
            f"Research Summary: {query}\n\n"
        ]
        
        # Overview section
        overview = "Overview: "
        if len(analyzed_contents) > 0:
            top_content = analyzed_contents[0]
            if 'key_sentences' in top_content and len(top_content['key_sentences']) > 0:
                overview += " ".join(top_content['key_sentences'][:2])
            else:
                overview += f"Based on research from {len(analyzed_contents)} sources."
        else:
            overview += "Insufficient information found on this topic."
            
        summary_parts.append(overview + "\n\n")
        
        # Add sections for each topic
        for topic, sentences in topics.items():
            if topic == 'other':
                section_title = "Additional Information"
            else:
                section_title = topic.title()
                
            summary_parts.append(f"{section_title}:\n")
            
            # Sort sentences by source relevance
            sentences.sort(key=lambda x: x['relevance'], reverse=True)
            
            # Take top sentences
            top_sentences = sentences[:5]  # Limit to 5 sentences per topic
            
            seen_texts = set()
            for sent_dict in top_sentences:
                sent_text = sent_dict['text'].strip()
                
                # Avoid duplicate sentences
                if sent_text in seen_texts:
                    continue
                seen_texts.add(sent_text)
                
                # Add sentence with source
                source_ref = f" ({sent_dict['source']})"
                summary_parts.append(f"- {sent_text}{source_ref}\n")
                
            summary_parts.append("\n")
        
        # Add information about gaps
        if 'gaps' in topics and topics['gaps']:
            summary_parts.append("Research Gaps:\n")
            for gap in topics['gaps']:
                summary_parts.append(f"- {gap['text']}\n")
            summary_parts.append("\n")
            
        return "".join(summary_parts)
    
    def _identify_key_findings(self, topics: Dict[str, List[Dict[str, str]]]) -> List[str]:
        """
        Identify key research findings.
        
        Args:
            topics: Dict of topics with associated sentences
            
        Returns:
            List of key findings
        """
        findings = []
        
        # Extract one key finding from each topic
        for topic, sentences in topics.items():
            if topic == 'other' or not sentences:
                continue
                
            # Sort by relevance and take the top sentence
            sentences.sort(key=lambda x: x['relevance'], reverse=True)
            top_sentence = sentences[0]['text']
            
            # Clean up the sentence
            top_sentence = top_sentence.strip()
            
            # Add topic context if not in sentence already
            if topic.lower() not in top_sentence.lower():
                finding = f"{topic.title()}: {top_sentence}"
            else:
                finding = top_sentence
                
            findings.append(finding)
            
        return findings[:5]  # Limit to 5 key findings
    
    def _suggest_further_research(self, query: str, analyzed_contents: List[Dict[str, Any]]) -> List[str]:
        """
        Suggest areas for further research.
        
        Args:
            query: Original research query
            analyzed_contents: List of analyzed content
            
        Returns:
            List of suggestions for further research
        """
        suggestions = []
        
        # Extract terms that appear frequently
        all_common_terms = []
        for content in analyzed_contents:
            if 'metadata' in content and 'common_terms' in content['metadata']:
                all_common_terms.extend(content['metadata']['common_terms'])
                
        # Count term frequency
        from collections import Counter
        term_counts = Counter(all_common_terms)
        
        # Generate suggestions based on common terms
        query_terms = query.lower().split()
        
        for term, count in term_counts.most_common(10):
            # Skip terms that are already in the query
            if term in query_terms or any(term in qt or qt in term for qt in query_terms):
                continue
                
            # Generate a suggestion
            suggestions.append(f"Explore the relationship between {query} and {term}")
            
            # Limit to 3 suggestions
            if len(suggestions) >= 3:
                break
                
        # Add generic suggestions if needed
        if len(suggestions) < 3:
            suggestions.append(f"Look into the latest developments in {query}")
            
        if len(suggestions) < 3:
            suggestions.append(f"Compare different perspectives on {query}")
            
        return suggestions[:3]  # Ensure max 3 suggestions
    
    def synthesize(self, query: str, analyzed_contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize analyzed content into a research report.
        
        Args:
            query: Original research query
            analyzed_contents: List of analyzed content
            
        Returns:
            Dict with synthesis results
        """
        logger.info(f"Synthesizing research findings for: {query}")
        
        if not analyzed_contents:
            logger.warning("No content to synthesize")
            return {
                'summary': f"No relevant information found for '{query}'.",
                'key_findings': [],
                'further_research': [
                    f"Try a different search query related to {query}",
                    "Use more specific keywords",
                    "Explore academic or specialized sources"
                ]
            }
        
        # Organize content by topic
        topics = self._organize_by_topic(analyzed_contents)
        
        # Create summary
        summary = self._create_summary(query, topics, analyzed_contents)
        
        # Identify key findings
        key_findings = self._identify_key_findings(topics)
        
        # Suggest further research
        further_research = self._suggest_further_research(query, analyzed_contents)
        
        logger.info("Synthesis complete")
        
        return {
            'summary': summary,
            'key_findings': key_findings,
            'further_research': further_research,
            'topics': list(topics.keys()),
            'sources': [{'url': content['url'], 'title': content['title']} 
                      for content in analyzed_contents]
        }