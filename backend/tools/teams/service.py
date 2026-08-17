# backend/tools/teams/service.py
import json
import uuid

from auth.delegated_auth import get_delegated_token, DelegatedAuthError
from clients.graph_client import graph_client, GraphClientError
from core.constants import GRAPH_CHATS_ENDPOINT, GRAPH_CHAT_MESSAGES_ENDPOINT
from tools.teams.exceptions import (
    AuthenticationError, PermissionDeniedError, ResourceNotFoundError,
    GraphServiceError, TeamsToolError,
)
from tools.teams.graph_users import resolve_user_id
from tools.teams.models import SendTeamsMessageRequest, SendTeamsMessageResponse
from tools.teams.parser import parse_send_teams_message_success
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

        chat_payload = {
            "chatType": "oneOnOne",
            "members": [
                {
                    "@odata.type": "#microsoft.graph.aadUserConversationMember",
                    "roles": ["owner"],
                    "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{caller_id}')",
                },
                {
                    "@odata.type": "#microsoft.graph.aadUserConversationMember",
                    "roles": ["owner"],
                    "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{recipient_id}')",
                },
            ],
        }
        chat_response = await graph_client.post(
            endpoint=GRAPH_CHATS_ENDPOINT, payload=chat_payload,
            correlation_id=correlation_id, access_token=access_token,
        )
        chat_id = chat_response.json()["id"]

        # Build the Adaptive Card and reference it from the message body
        # via Graph's required <attachment id="..."></attachment> pattern.
        safe_body = ensure_html_body(request.message)
        card = build_teams_adaptive_card(title="New Message", body_html=safe_body)
        attachment_id = str(uuid.uuid4())

        message_payload = {
            "body": {
                "contentType": "html",
                "content": f'<attachment id="{attachment_id}"></attachment>',
            },
            "attachments": [
                {
                    "id": attachment_id,
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": json.dumps(card),
                }
            ],
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