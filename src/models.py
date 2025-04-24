"""
Data models for the research agent.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class SearchResult:
    """Data model for search results."""
    title: str
    url: str
    snippet: str
    source: str  # Which search engine provided this result

@dataclass
class ScrapedContent:
    """Data model for scraped web content."""
    url: str
    title: str
    content: str
    meta_description: str = ""
    html: str = ""  # Raw HTML content
    scrape_time: datetime = field(default_factory=datetime.now)

@dataclass
class AnalyzedContent:
    """Data model for analyzed content."""
    url: str
    title: str
    relevance_score: float
    key_sentences: List[str]
    metadata: Dict[str, Any]
    content: str  # Full content

@dataclass
class TopicCluster:
    """Data model for a cluster of related content."""
    topic: str
    sentences: List[Dict[str, Any]]
    sources: List[str]
    relevance: float

@dataclass
class ResearchSynthesis:
    """Data model for the final research synthesis."""
    query: str
    summary: str
    key_findings: List[str]
    further_research: List[str]
    topics: List[str]
    sources: List[Dict[str, str]]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ResearchHistory:
    """Data model for tracking research history."""
    query: str
    timestamp: datetime
    duration_seconds: float
    sources_count: int
    result_id: str  # Reference to stored result

@dataclass
class ResearchRequest:
    """Data model for research requests."""
    query: str
    depth: int = 3
    max_sources: int = 10
    timeout_seconds: int = 60
    user_id: Optional[str] = None