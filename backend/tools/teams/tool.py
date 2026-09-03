# backend/tools/teams/tool.py
import json
from typing import Annotated

from pydantic import Field
from agent_framework import tool

from core.enums import ToolName
from dispatcher.tool_dispatcher import tool_dispatcher
from tools.teams.draft_store import save_draft, get_draft, clear_draft
from tools.teams.exceptions import TeamsToolError
from tools.teams.models import SendTeamsMessageRequest, SendTeamsMessageResponse
from tools.teams.service import send_teams_message as send_teams_message_service
from tools.teams.validator import validate_send_teams_message_request
from utils.correlation import generate_correlation_id
from utils.logger import get_logger
from utils.response import error_response

logger = get_logger(__name__)


async def execute_send_teams_message(raw_args: dict, logged_in_user_email: str) -> dict:
    """
    Internal business entry point — actually calls Graph. Builds the
    recipient-facing card (with content-approval buttons) internally
    via send_teams_message_service — see tools/teams/service.py.
    """
    correlation_id = generate_correlation_id()

    try:
        request = SendTeamsMessageRequest(**raw_args)
    except Exception as e:
        logger.warning(f"[{correlation_id}] Invalid send_teams_message arguments: {e}")
        return error_response(message=f"Invalid input: {str(e)}", status_code=400, request_id=correlation_id)

    try:
        validate_send_teams_message_request(request)
        result: SendTeamsMessageResponse = await send_teams_message_service(
            request=request, logged_in_user_email=logged_in_user_email, correlation_id=correlation_id,
        )
        return result.model_dump()

    except TeamsToolError as e:
        logger.error(f"[{correlation_id}] TeamsToolError: {e.message}")
        return error_response(message=e.message, status_code=e.status_code, request_id=correlation_id, retryable=e.retryable)

    except Exception:
        logger.exception(f"[{correlation_id}] Unhandled error in execute_send_teams_message.")
        return error_response(message="An unexpected error occurred while sending the Teams message.", status_code=500, request_id=correlation_id, retryable=True)


async def resolve_teams_draft(user_email: str, approved: bool) -> dict:
    """
    Shared resolution logic used by confirm_send_teams_message (chat
    "approve"/"decline" by the SENDER, before anything reaches the
    recipient). This is the send-gate — separate from the recipient's
    later content-approval click, which is handled in
    router/teams_actions.py via notify_sender_of_response, not here.
    """
    correlation_id = generate_correlation_id()
    draft = get_draft(user_email)

    if draft is None:
        return {"status": "no_draft", "message": "There is no pending draft to confirm."}

    clear_draft(user_email)

    if not approved:
        logger.info(f"TEAMS DRAFT DECLINED | user={user_email}")
        return {"status": "declined", "message": "The Teams message was not sent."}

    logger.info(f"TEAMS DRAFT APPROVED, SENDING | user={user_email}")
    result = await tool_dispatcher.dispatch(ToolName.SEND_TEAMS_MESSAGE.value, draft, user_email)
    logger.info(f"TEAMS SEND RESULT | user={user_email} | {result}")
    return result


def make_teams_tools(logged_in_user_email: str) -> list:

    @tool(
        name="draft_teams_message",
        description=(
            "Stage a draft Teams message for the SENDER to review before "
            "sending. This does NOT send it — only prepares it for the "
            "sender's own approval. Always use this first when asked to "
            "send a Teams message."
        ),
    )
    async def draft_teams_message(
        recipient: Annotated[str, Field(description="Recipient's email address. If the user says 'me', use the logged-in user's own email.")],
        message: Annotated[str, Field(description="The Teams message text.")],
    ) -> str:
        draft = {"recipient": recipient, "message": message}
        save_draft(logged_in_user_email, draft)

        logger.info(f"TEAMS DRAFT CREATED | user={logged_in_user_email} | to={recipient}")
        return json.dumps({
            "status": "draft_ready",
            "message": "Draft prepared. Show this to the user and ask them to approve or decline.",
            "draft": draft,
        })

    @tool(
        name="confirm_send_teams_message",
        description=(
            "Send the previously staged draft, or discard it. Only call "
            "AFTER the SENDER (the logged-in user) has explicitly approved "
            "or declined in chat. This is the sender's own send-gate — "
            "separate from the recipient's later response to the message "
            "content once it's delivered."
        ),
    )
    async def confirm_send_teams_message(
        approved: Annotated[bool, Field(description="True if the sender approved sending, False if they declined.")],
    ) -> str:
        result = await resolve_teams_draft(logged_in_user_email, approved)
        return json.dumps(result)

    return [draft_teams_message, confirm_send_teams_message]