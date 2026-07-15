import os
from dotenv import load_dotenv

load_dotenv()

# URL configuration
API_HOST = os.getenv("HOST_URL", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
API_URL = f"http://{API_HOST}:{API_PORT}"

# LLM configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL_ID = "gemini-2.5-flash"  # default model ID, can be changed as needed

# retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 8.0

