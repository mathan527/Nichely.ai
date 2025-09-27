from pydantic_settings import BaseSettings
import aiohttp
from base64 import b64encode
import os

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    # Reddit API
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USERNAME: str = "YourRedditUsername"
    REDDIT_PASSWORD: str = "YOUR_PASSWORD_HERE"
    REDDIT_USER_AGENT: str = "NichelyApp/1.0"
    
    # AI API Keys
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str = ""
    GROQ_PRIMARY_MODEL: str = "meta-llama/llama-guard-4-12b"
    GROQ_BACKUP_MODEL: str = "openai/gpt-oss-120b"
    GROQ_MAX_TOKENS: int = 5000
    
    # Server Configuration
    PORT: int = "Add your port"
    HOST: str = "0.0.0.0"
    
    # Market Data API
    # MARKET_DATA_KEY: str = ""

    def validate_reddit_credentials(self) -> bool:
        """Check if all Reddit credentials are set for authenticated access"""
        return all([
            self.REDDIT_CLIENT_ID,
            self.REDDIT_CLIENT_SECRET,
            self.REDDIT_USERNAME,
            self.REDDIT_PASSWORD
        ])

    def get_reddit_auth_headers(self) -> dict:
        """Get Reddit API headers based on available credentials"""
        headers = {"User-Agent": self.REDDIT_USER_AGENT}
        
        # If we have credentials, add authorization
        if self.validate_reddit_credentials():
            credentials = f"{self.REDDIT_CLIENT_ID}:{self.REDDIT_CLIENT_SECRET}"
            auth = b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {auth}"
            
        return headers

settings = Settings()
