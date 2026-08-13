# backend/tools/teams/parser.py

from core.enums import ResponseStatus
from tools.teams.models import SendTeamsMessageResponse


def parse_send_teams_message_success(
    *,
    status_code: int,
    request_id: str,
) -> SendTeamsMessageResponse:
    """
    Parses a successful Microsoft Graph response into the
    standard Teams response model.
    """

    return SendTeamsMessageResponse(
        success=True,
        status=ResponseStatus.SUCCESS,
        status_code=status_code,
        message="Teams message sent successfully.",
        request_id=request_id,
        retryable=False,
    )


def parse_send_teams_message_error(
    *,
    status_code: int,
    request_id: str,
    message: str,
    retryable: bool = False,
) -> SendTeamsMessageResponse:
    """
    Parses a failed Microsoft Graph response into the
    standard Teams response model.
    """

    return SendTeamsMessageResponse(
        success=False,
        status=ResponseStatus.FAILED,
        status_code=status_code,
        message=message,
        request_id=request_id,
        retryable=retryable,
    )