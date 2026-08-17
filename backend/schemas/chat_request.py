# backend/schemas/chat_request.py
from pydantic import BaseModel, Field, ConfigDict


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str
    content: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(..., min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)