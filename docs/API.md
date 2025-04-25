# AI Web Research Agent API Documentation

## ResearchAgent

### Methods

#### research(query: str) -> str
Performs comprehensive research on the given query.

Parameters:
- query: Research question or topic

Returns:
- Formatted research report

#### analyze_query(query: str) -> List[str]
Analyzes and expands the research query.

Parameters:
- query: Original query string

Returns:
- List of expanded search queries

## SearchTool

### Methods

#### direct_search(query: str, max_results: int = 3) -> List[Dict]
Performs web search using the query.

Parameters:
- query: Search query
- max_results: Maximum number of results to return

Returns:
- List of search results with URLs and snippets