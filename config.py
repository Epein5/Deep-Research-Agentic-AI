from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """Configuration class to manage environment variables and constants."""
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    GOOGLE_STUDIO_API_KEY = os.getenv("GOOGLE_STUDIO_API_KEY")
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

config = Config()