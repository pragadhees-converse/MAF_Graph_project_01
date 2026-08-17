# core/settings.py
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# project-root/.env  (one level above backend/)
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """
    Loaded from project-root/.env. NEVER imported inside agents/,
    dispatcher/, or tools/*/tool.py — only auth/ and clients/ may read this.
    """

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    # ---- Azure AI Foundry (Azure OpenAI) ----
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_DEPLOYMENT: str

    # ---- Microsoft Graph (Azure AD app registration) ----
    AZURE_AD_CLIENT_ID: str
    AZURE_AD_TENANT_ID: str
    AZURE_AD_CLIENT_SECRET: str
    AZURE_AD_REDIRECT_URI: str
    SESSION_SECRET_KEY: str

    APP_ENV: str = "dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()