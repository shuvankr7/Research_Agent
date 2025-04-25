# AI Web Research Agent 

An intelligent web research assistant that automatically searches, analyzes, and synthesizes information from across the internet to create comprehensive research reports.
## App link - https://researchagent-tbbjlfwy497vfsn2pwjjno.streamlit.app/

##  Features

-  Intelligent Query Analysis
  - Smart query expansion
  - Context-aware search
  - Topic categorization

-  Advanced Web Search
  - Multi-source search
  - Priority-based source ranking
  - Real-time content fetching
  - Robots.txt compliance

-  News Aggregation
  - Latest news integration
  - Trusted source prioritization
  - Time-sensitive content filtering

-  Content Processing
  - Smart content extraction
  - Source validation
  - Information synthesis
  - Duplicate removal

-  Report Generation
  - Structured research reports
  - Source citations
  - Content organization
  - Summary generation

##  Getting Started

### Prerequisites
- Python 3.8+
- Groq API key
- Internet connection

### Installation

1. Clone the repository:
```
git clone https://github.com/shuvankr7/Research_Agent.git
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Set up environment variables:

Create a .env file with:
GROQ_API_KEY=your_api_key_here
SERPER_API_KEY=your_serper_api_key

### Usage
Run the web interface:
streamlit run app.py

## 🏗 Project Structure

```ai-web-research-agent/
├── src/
│   ├── agents/
│   │   └── research_agent.py
│   ├── tools/
│   │   ├── search_tool.py
│   │   ├── news_aggregator.py
│   │   ├── robots_checker.py
│   │   └── cache_manager.py
│   └── utils/
│       ├── config.py
│       └── logger.py
├── tests/
│   └── test_research_agent.py
├── app.py
└── requirements.txt
```

##  Flow Diagram
```graph TD
    A[User Query] --> B[Query Analysis]
    B --> C[Search Terms Generation]
    C --> D[Web Search]
    D --> E[Content Extraction]
    E --> F[Content Analysis]
    F --> G[Report Generation]
    G --> H[Final Report]
    
    D --> I[News Search]
    I --> F
    
    E --> J{Robots.txt Check}
    J -->|Allowed| F
    J -->|Not Allowed| K[Skip Source]
```

##  License
This project is licensed under the MIT License - see the LICENSE file for details.

##  Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

