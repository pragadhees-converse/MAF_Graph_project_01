# backend/tools/teams/service.py
import json
import uuid

from auth.delegated_auth import get_delegated_token, DelegatedAuthError
from auth.token_manager import token_manager
from clients.graph_client import graph_client, GraphClientError
from core.constants import (
    GRAPH_CHATS_ENDPOINT,
    GRAPH_CHAT_MESSAGES_ENDPOINT,
    GRAPH_SEND_TEAMS_NOTIFICATION_ENDPOINT,
    TENANT_ID,
)
from core.settings import get_settings
from tools.teams.exceptions import (
    AuthenticationError, PermissionDeniedError, ResourceNotFoundError,
    GraphServiceError, TeamsToolError,
)
from tools.teams.graph_users import resolve_user_id
from tools.teams.models import SendTeamsMessageRequest, SendTeamsMessageResponse
from tools.teams.parser import parse_send_teams_message_success
from utils.action_tokens import create_action_token
from utils.adaptive_card import build_teams_adaptive_card
from utils.html_format import ensure_html_body
from utils.logger import get_logger

logger = get_logger(__name__)


async def send_teams_message(
    request: SendTeamsMessageRequest, logged_in_user_email: str, correlation_id: str
) -> SendTeamsMessageResponse:
    try:
        access_token = await get_delegated_token(logged_in_user_email)
    except DelegatedAuthError as e:
        raise AuthenticationError(e.message)

    try:
        recipient_id = await resolve_user_id(request.recipient, access_token, correlation_id)
        caller_id = await resolve_user_id(logged_in_user_email, access_token, correlation_id)
        member_ids = {caller_id, recipient_id}

        chat_payload = {
            "chatType": "oneOnOne",
            "members": [
                {
                    "@odata.type": "#microsoft.graph.aadUserConversationMember",
                    "roles": ["owner"],
                    "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{uid}')",
                }
                for uid in member_ids
            ],
        }
        chat_response = await graph_client.post(
            endpoint=GRAPH_CHATS_ENDPOINT, payload=chat_payload,
            correlation_id=correlation_id, access_token=access_token,
        )
        chat_id = chat_response.json()["id"]

        # These tokens represent GOKUL's decision on the CONTENT — not a
        # send-gate (sending already happened via chat approval). Clicking
        # either one notifies the original sender of the outcome.
        settings = get_settings()
        summary = request.message[:100]

        approve_token = create_action_token({
            "kind": "content_response",
            "sender_email": logged_in_user_email,
            "recipient_email": request.recipient,
            "summary": summary,
            "decision": "approve",
        })
        decline_token = create_action_token({
            "kind": "content_response",
            "sender_email": logged_in_user_email,
            "recipient_email": request.recipient,
            "summary": summary,
            "decision": "decline",
        })
        approve_url = f"{settings.APP_BASE_URL}/teams-action?token={approve_token}"
        decline_url = f"{settings.APP_BASE_URL}/teams-action?token={decline_token}"

        safe_body = ensure_html_body(request.message)
        card = build_teams_adaptive_card(
            title="New Message — Please Review",
            body_html=safe_body,
            approve_url=approve_url,
            decline_url=decline_url,
        )
        attachment_id = str(uuid.uuid4())

        message_payload = {
            "body": {"contentType": "html", "content": f'<attachment id="{attachment_id}"></attachment>'},
            "attachments": [{
                "id": attachment_id,
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": json.dumps(card),
            }],
        }
        response = await graph_client.post(
            endpoint=GRAPH_CHAT_MESSAGES_ENDPOINT.format(chat_id=chat_id),
            payload=message_payload, correlation_id=correlation_id, access_token=access_token,
        )

    except GraphClientError as e:
        logger.error(f"[{correlation_id}] Graph error {e.status_code}: {e.message}")
        raise _translate_graph_error(e, request.recipient)
    except Exception as e:
        logger.exception(f"[{correlation_id}] Unexpected error sending Teams message.")
        raise GraphServiceError(f"Unexpected error: {str(e)}")

    result = parse_send_teams_message_success(response, correlation_id)
    return SendTeamsMessageResponse(**result)


async def notify_sender_of_response(sender_email: str, recipient_email: str, summary: str, decision: str, correlation_id: str) -> None:
    """
    Notifies the original sender that the recipient responded, using
    app-only TeamsActivity.Send — the correct tool here since this is
    a system-originated notification, not attributable to any person.
    """
    caller_id = await resolve_user_id(sender_email, None, correlation_id, use_app_only=True)
    payload = {
        "topic": {"source": "text", "value": "Response Received"},
        "activityType": "systemDefault",
        "previewText": {"content": f"{recipient_email} {decision}d: {summary}"},
        "templateParameters": [{"name": "systemUser", "value": "Assistant"}],
    }
    await graph_client.post(
        endpoint=GRAPH_SEND_TEAMS_NOTIFICATION_ENDPOINT.format(user_id=sender_email),
        payload=payload,
        tenant_id=TENANT_ID,
        correlation_id=correlation_id,
    )


def _translate_graph_error(error, recipient) -> TeamsToolError:
    if error.status_code == 401:
        return AuthenticationError()
    if error.status_code == 403:
        return PermissionDeniedError()
    if error.status_code == 404:
        return ResourceNotFoundError(recipient)
    if error.status_code == 400:
        return TeamsToolError(error.message, status_code=400, retryable=False)
    return GraphServiceError(error.message, status_code=error.status_code)