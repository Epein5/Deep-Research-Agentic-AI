# config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """Configuration class to manage environment variables and constants."""
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


config = Config()