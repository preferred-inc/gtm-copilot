from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    GTM_CLIENT_ID: str = ""
    GTM_CLIENT_SECRET: str = ""
    GTM_REFRESH_TOKEN: str = ""
    ANTHROPIC_API_KEY: str = ""
    FRONTEND_URL: str = "http://localhost:3000"
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/auth/callback"

    model_config = {
        "env_file": os.path.join(os.path.dirname(__file__), '..', '..', 'src', '.env'),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()
