# backend/services/chat_service.py
from agents.graph_agent import graph_agent
from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from utils.correlation import generate_correlation_id
from utils.logger import get_logger

logger = get_logger(__name__)


async def handle_chat(request: ChatRequest) -> ChatResponse:
    """
    Entry point for a chat turn. Converts API-level history format
    into the plain dict format the agent expects, invokes the agent,
    and wraps the result in a standardized ChatResponse.
    """
    correlation_id = generate_correlation_id()
    logger.info(f"[{correlation_id}] Handling chat request.")

    conversation_history = [
        {"role": m.role, "content": m.content} for m in request.history
    ]

    reply = await graph_agent.run(
        user_message=request.message,
        conversation_history=conversation_history,
    )

    return ChatResponse(reply=reply, request_id=correlation_id)