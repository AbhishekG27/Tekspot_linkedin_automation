"""Load config from environment."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TOPICS_EXCEL = DATA_DIR / "topics.xlsx"
OUTPUT_DIR = BASE_DIR / "output"

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

# Gemini (chat: topics + content)
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3-flash-preview")

# Gemini (images: Imagen) — use imagen-4.0-generate-001 for Gemini API
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "imagen-4.0-generate-001")


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
