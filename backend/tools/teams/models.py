# backend/tools/teams/models.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class SendTeamsMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipient: EmailStr = Field(..., description="Recipient's email address.")
    message: str = Field(..., min_length=1, max_length=4000)


class SendTeamsMessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    status_code: int
    message: str
    request_id: str
    retryable: bool = False