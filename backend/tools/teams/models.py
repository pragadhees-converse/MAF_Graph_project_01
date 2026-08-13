# backend/tools/teams/models.py

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core.enums import ResponseStatus


class SendTeamsMessageRequest(BaseModel):
    """
    Internal request model used throughout the Teams
    message pipeline.

    This model is created after the LLM invokes the
    send_teams_message tool and before any Graph API
    call is made.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    recipient: EmailStr = Field(
        ...,
        description="Recipient's Microsoft 365 email address.",
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Teams message content.",
    )


class SendTeamsMessageResponse(BaseModel):
    """
    Standard response returned from every Teams
    message execution.

    No raw Microsoft Graph response should ever
    leave the service layer.
    """

    success: bool

    status: ResponseStatus

    status_code: int

    message: str

    request_id: str

    retryable: bool = False