# backend/agents/base_agent.py
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    @abstractmethod
    async def run(self, user_message: str, conversation_history: list[dict] | None = None) -> str:
        ...