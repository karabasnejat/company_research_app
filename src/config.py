import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Model Configuration
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", "10"))
    
    # Validation
    @classmethod
    def validate_config(cls):
        """Validate that required environment variables are set"""
        missing_vars = []
        
        if not cls.OPENAI_API_KEY:
            missing_vars.append("OPENAI_API_KEY")
        
        if not cls.TAVILY_API_KEY:
            missing_vars.append("TAVILY_API_KEY")
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Search Configuration
    SEARCH_TIMEOUT = 30  # seconds
    MAX_CONCURRENT_SEARCHES = 5
