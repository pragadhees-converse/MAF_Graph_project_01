# backend/clients/llm_client.py
from agent_framework.openai import OpenAIChatClient

from core.settings import get_settings


def get_chat_client() -> OpenAIChatClient:
    """
    Factory for the chat client used by the agent.

    NOTE: In the currently installed agent-framework version,
    agent_framework.azure.AzureOpenAIChatClient no longer exists —
    Azure OpenAI is routed through agent_framework.openai.OpenAIChatClient
    by passing azure_endpoint (this is what triggers Azure routing
    instead of plain OpenAI routing). `model` here is your Azure
    deployment name, not an OpenAI model name.
    """
    settings = get_settings()
    return OpenAIChatClient(
        model=settings.AZURE_OPENAI_DEPLOYMENT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )