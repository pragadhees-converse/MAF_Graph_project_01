# backend/router/chat.py
from fastapi import APIRouter, HTTPException, Request

from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from services.chat_service import handle_chat
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: Request, body: ChatRequest) -> ChatResponse:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in.")

    try:
        return await handle_chat(body, logged_in_user_email=user["email"])
    except Exception:
        logger.exception("Unhandled error in /chat endpoint.")
        raise HTTPException(status_code=500, detail="Internal server error.")