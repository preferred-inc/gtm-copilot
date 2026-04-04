import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: Literal["development", "production"] = "development"
    GTM_CLIENT_ID: str = ""
    GTM_CLIENT_SECRET: str = ""
    GTM_REFRESH_TOKEN: str = ""
    ANTHROPIC_API_KEY: str = ""
    FRONTEND_URL: str = "http://localhost:3000"
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/auth/callback"
    CORS_ORIGINS: str = ""  # comma-separated, overrides FRONTEND_URL if set
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    def validate_required(self) -> list[str]:
        """Return list of missing required settings for production."""
        missing = []
        for key in ("GTM_CLIENT_ID", "GTM_CLIENT_SECRET", "GTM_REFRESH_TOKEN", "ANTHROPIC_API_KEY"):
            if not getattr(self, key):
                missing.append(key)
        return missing

    model_config = {
        "env_file": os.path.join(os.path.dirname(__file__), '..', '..', 'src', '.env'),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()
