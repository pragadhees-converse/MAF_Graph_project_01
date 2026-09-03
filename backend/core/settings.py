# backend/core/settings.py
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# project-root/.env  (one level above backend/)
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """
    Loaded from project-root/.env. NEVER imported inside agents/,
    dispatcher/, or tools/*/tool.py's business logic — only auth/,
    clients/, and the specific tool factories that need to build
    absolute URLs (e.g. tools/teams/tool.py for action button links)
    may read this.
    """

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    # ---- Azure AI Foundry (Azure OpenAI) ----
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_DEPLOYMENT: str

    # ---- Microsoft Graph / Azure AD (Azure AD app registration) ----
    AZURE_AD_CLIENT_ID: str
    AZURE_AD_TENANT_ID: str
    AZURE_AD_CLIENT_SECRET: str
    AZURE_AD_REDIRECT_URI: str

    # ---- Session / auth ----
    SESSION_SECRET_KEY: str

    # ---- Application ----
    APP_BASE_URL: str = "http://localhost:8000"
    APP_ENV: str = "dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()