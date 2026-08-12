# backend/schemas/chat_request.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str
    content: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)
    user_email: EmailStr = Field(..., description="The logged-in user's email, from Streamlit login.")