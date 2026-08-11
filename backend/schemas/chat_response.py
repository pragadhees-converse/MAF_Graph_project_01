# backend/schemas/chat_response.py
from pydantic import BaseModel, ConfigDict


class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply: str
    request_id: str