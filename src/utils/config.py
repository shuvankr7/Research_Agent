import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
MAX_RESULTS = 5
DEFAULT_TIMEOUT = 10  # seconds
MIN_DELAY_BETWEEN_REQUESTS = 1.0  # seconds

# API Keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

# LLM Model
DEFAULT_MODEL = "llama3-70b-8192"

# Cache settings
CACHE_DIR = "cache"
NEWS_CACHE_EXPIRY_HOURS = 1
DEFAULT_CACHE_EXPIRY_HOURS = 24