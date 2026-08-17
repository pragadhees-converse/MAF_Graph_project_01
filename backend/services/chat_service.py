# backend/services/chat_service.py
from agents.graph_agent import graph_agent
from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from utils.correlation import generate_correlation_id
from utils.logger import get_logger

logger = get_logger(__name__)


async def handle_chat(request: ChatRequest, logged_in_user_email: str) -> ChatResponse:
    correlation_id = generate_correlation_id()
    logger.info(f"[{correlation_id}] Chat request | user={logged_in_user_email} | message='{request.message}'")

    conversation_history = [{"role": m.role, "content": m.content} for m in request.history]

    reply = await graph_agent.run(
        user_message=request.message,
        logged_in_user_email=logged_in_user_email,
        conversation_history=conversation_history,
    )

    logger.info(f"[{correlation_id}] Chat response | user={logged_in_user_email} | reply='{reply}'")
    return ChatResponse(reply=reply, request_id=correlation_id)