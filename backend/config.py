import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Find the project's root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# API configuration
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Initialize Gemini client
def get_client():
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is missing.")

    return genai.Client(api_key=API_KEY)
