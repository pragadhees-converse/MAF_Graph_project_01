# backend/agents/graph_agent.py
from agent_framework import Agent

from agents.base_agent import BaseAgent
from agents.system_prompt import SYSTEM_PROMPT
from clients.llm_client import get_chat_client
from tools.definitions import ALL_TOOLS
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphAgent(BaseAgent):
    """
    Wraps Agent Framework's Agent class (this version has no ChatAgent —
    the older docs describing ChatAgent don't match the installed
    1.13.0 API, confirmed by inspecting the package directly).
    """

    def __init__(self):
        self._agent = Agent(
            client=get_chat_client(),
            name="GraphMailAgent",
            instructions=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
        )

    async def run(self, user_message: str, conversation_history: list[dict] | None = None) -> str:
        logger.info("Running GraphAgent for a new user message.")
        result = await self._agent.run(user_message)
        return result.text


# Singleton shared across the app
graph_agent = GraphAgent()