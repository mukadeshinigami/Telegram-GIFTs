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
        """Fallback config if pydantic BaseSettings is not available.

        This keeps the project runnable in minimal environments.
        """

        def __init__(self) -> None:
            self.BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
            self.API_URL: str = os.getenv("API_URL", "http://127.0.0.1:8000")
            self.DB_PATH: Optional[str] = os.getenv("DB_PATH")