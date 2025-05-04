"""
Configuration settings for the application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Settings
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

# Document Settings
DOCUMENT_PATH = os.getenv("DOCUMENT_PATH", "data/insurance_regulations.txt")

# Database Settings
DB_PATH = os.getenv("DB_PATH", "db/chroma_db")

# Text Splitter Settings
CHUNK_SIZE = 200
CHUNK_OVERLAP = 50

# OpenAI Base URL - Add this new configuration
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")  # Default to standard OpenAI endpoint

