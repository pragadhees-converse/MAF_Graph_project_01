# backend/tools/mail/models.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from core.enums import Importance


class SendMailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipient: EmailStr = Field(..., description="Recipient's email address.")
    subject: str = Field(..., min_length=1, max_length=150)
    body: str = Field(..., min_length=1, max_length=20000)
    importance: Importance = Field(default=Importance.NORMAL)
    save_to_sent_items: bool = Field(default=True)


class SendMailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    status_code: int
    message: str
    request_id: str
    retryable: bool = False