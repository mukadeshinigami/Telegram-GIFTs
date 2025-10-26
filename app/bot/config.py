from typing import Optional
import os


try:
    from pydantic_settings import BaseSettings  
except Exception:
    try:
        from pydantic import BaseSettings  
    except Exception:
        BaseSettings = None  


if BaseSettings is not None:
    class Config(BaseSettings):
        
        """Application configuration read from environment (or from a local .env file)."""

        BOT_TOKEN: Optional[str] = None
        API_URL: str = "http://127.0.0.1:8000"
        DB_PATH: Optional[str] = None

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"


else:
    class Config:
        
        """Configuration class for the Telegram bot application.

        This class serves as a fallback configuration loader when pydantic BaseSettings
        is not available, ensuring the project remains functional in minimal environments.

        Attributes:
            BOT_TOKEN (Optional[str]): Telegram bot token from environment variable 'BOT_TOKEN'.
                Required for bot authentication with Telegram API.
            API_URL (str): Base URL for the API service. Defaults to 'http://127.0.0.1:8000'
                if 'API_URL' environment variable is not set.
            DB_PATH (Optional[str]): Path to the database file from environment variable 'DB_PATH'.
                If not provided, the application may use default database settings.

        Environment Variables:
            BOT_TOKEN: Telegram bot token (required)
            API_URL: API service URL (optional, defaults to localhost:8000)
            DB_PATH: Database file path (required)
        """
        
        def __init__(self) -> None:
            self.BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
            self.API_URL: str = os.getenv("API_URL", "http://127.0.0.1:8000")
            self.DB_PATH: Optional[str] = os.getenv("DB_PATH")