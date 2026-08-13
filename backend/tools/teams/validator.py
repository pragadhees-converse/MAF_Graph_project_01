from tools.teams.errors import TeamsValidationError
from tools.teams.models import SendTeamsMessageRequest

from core.constants import (
    COMPANY_DOMAIN,
    BODY_MAX_LENGTH,
)

from utils.logger import get_logger

logger = get_logger(__name__)


def validate_send_teams_message_request(
    request: SendTeamsMessageRequest,
    logged_in_user_email: str,
) -> None:
    """
    Business validation before any Microsoft Graph calls.

    Pydantic validates:
        - Required fields
        - Types
        - Enum values

    This validator enforces business rules.
    """

    logger.info(
        f"Validating Teams message request for '{logged_in_user_email}'."
    )

    # -------------------------------------------------------
    # Only allow sending to the logged-in user.
    # -------------------------------------------------------

    if request.recipient.lower() != logged_in_user_email.lower():
        raise TeamsValidationError(
            "Teams messages can only be sent to the logged-in user."
        )

    # -------------------------------------------------------
    # Recipient must belong to the company.
    # -------------------------------------------------------

    if not request.recipient.lower().endswith(
        f"@{COMPANY_DOMAIN}"
    ):
        raise TeamsValidationError(
            f"Recipient must belong to '{COMPANY_DOMAIN}'."
        )

    # -------------------------------------------------------
    # Empty message.
    # -------------------------------------------------------

    if not request.message.strip():
        raise TeamsValidationError(
            "Message cannot be empty."
        )

    # -------------------------------------------------------
    # Maximum size.
    # -------------------------------------------------------

    if len(request.message) > BODY_MAX_LENGTH:
        raise TeamsValidationError(
            f"Message exceeds {BODY_MAX_LENGTH} characters."
        )

    logger.info("Teams message validation completed successfully.")