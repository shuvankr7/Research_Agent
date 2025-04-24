# AI Web Research Agent 🔍

An intelligent web research assistant that automatically searches, analyzes, and synthesizes information from the web using advanced AI technologies.

## Features

- 🌐 Smart web searching with rate limiting
- ⚡ Real-time content analysis
- 🔄 Automatic URL validation
- 📊 Time-sensitive search capabilities
- 💡 Intelligent error handling
- 🖥️ Web interface with Streamlit

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Serper API key
- Groq API key

### Installation

1. Clone the repository:

git clone https://github.com/shuvankr7/research.git
cd research

2. Create a .env file and add your API keys:

SERPER_API_KEY=your_serper_api_key
GROQ_API_KEY=your_groq_api_key

3. Install required packages:

pip install -r requirements.txt

## Usage
### Web Interface
Launch the Streamlit app:

streamlit run aapp.py

### Command Line
Run research directly from terminal:

python main.py --query "your research question"

## Project Structure

ai-web-research-agent/
├── src/
│   ├── agents/
│   │   └── research_agent.py
│   ├── tools/
│   │   ├── search_tool.py
│   │   ├── content_processor.py
│   │   └── cache_manager.py
│   └── utils/
│       ├── config.py
│       └── logger.py
├── main.py
├── aapp.py
└── README.md

## Key Components
### Search Tool
- Implements rate-limited web searching
- Handles API throttling gracefully
- Validates and cleans URLs
- Supports time-sensitive queries
### Research Agent
- Processes and analyzes search results
- Generates comprehensive reports
- Manages content caching
- Handles multiple search queries
## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
## License
This project is licensed under the MIT License.
