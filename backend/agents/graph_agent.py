# backend/agents/graph_agent.py
from agent_framework import Agent, Message

from agents.base_agent import BaseAgent
from agents.system_prompt import SYSTEM_PROMPT
from clients.llm_client import get_chat_client
from tools.definitions import get_tools_for_user
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphAgent(BaseAgent):
    async def run(
        self,
        user_message: str,
        logged_in_user_email: str,
        conversation_history: list[dict] | None = None,
    ) -> str:
        logger.info(f"Agent run started | user={logged_in_user_email} | message='{user_message}'")

        # Build the full message list: prior turns + this new message.
        # Without this, every message is treated as a brand-new
        # conversation with zero memory of drafts, prior answers, or
        # anything the user said before — which is exactly why "approve"
        # failed: the agent genuinely had no idea a draft existed.
        messages: list[Message] = []
        for turn in (conversation_history or []):
            messages.append(Message(role=turn["role"], contents=[turn["content"]]))
        messages.append(Message(role="user", contents=[user_message]))

        agent = Agent(
            client=get_chat_client(),
            name="GraphAssistant",
            instructions=SYSTEM_PROMPT,
            tools=get_tools_for_user(logged_in_user_email),
        )

        result = await agent.run(messages)

        logger.info(f"Agent reply | user={logged_in_user_email} | reply='{result.text}'")

        return result.text


graph_agent = GraphAgent()