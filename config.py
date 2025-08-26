from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """Configuration class to manage environment variables and constants."""
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
    GOOGLE_STUDIO_API_KEY = os.getenv("GOOGLE_STUDIO_API_KEY", "").strip()
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "").strip()
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "").strip()
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

config = Config()