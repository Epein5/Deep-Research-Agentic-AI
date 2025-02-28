from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """Configuration class to manage environment variables and constants."""
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    GOOGLE_STUDIO_API_KEY = os.getenv("GOOGLE_STUDIO_API_KEY")
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

config = Config()