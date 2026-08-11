# backend/router/chat.py
from fastapi import APIRouter, HTTPException

from schemas.chat_request import ChatRequest
from schemas.chat_response import ChatResponse
from services.chat_service import handle_chat
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    try:
        return await handle_chat(request)
    except Exception as e:
        logger.exception("Unhandled error in /chat endpoint.")
        raise HTTPException(status_code=500, detail="Internal server error.")