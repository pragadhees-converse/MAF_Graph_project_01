from clients.graph_client import GraphClientError, graph_client

from core.constants import (
    GRAPH_BASE_URL,
    GRAPH_USERS_ENDPOINT,
    GRAPH_CHATS_ENDPOINT,
    GRAPH_CHAT_MESSAGES_ENDPOINT,
    TENANT_ID,
)

from tools.teams.builder import build_send_teams_message_payload
from tools.teams.models import (
    SendTeamsMessageRequest,
    SendTeamsMessageResponse,
)
from tools.teams.parser import (
    parse_send_teams_message_error,
    parse_send_teams_message_success,
)

from utils.logger import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------------
# Resolve Recipient
# ------------------------------------------------------------------

async def _get_user_id(
    *,
    recipient: str,
    correlation_id: str,
) -> str:
    """
    Resolves a recipient email address into a Microsoft Graph User ID.
    """

    logger.info(
        f"[{correlation_id}] STEP 1 - Resolving recipient '{recipient}'."
    )

    endpoint = GRAPH_USERS_ENDPOINT.format(
        user_principal_name=recipient,
    )

    response = await graph_client.get(
        endpoint=endpoint,
        tenant_id=TENANT_ID,
        correlation_id=correlation_id,
    )

    logger.info(
        f"[{correlation_id}] User lookup returned HTTP {response.status_code}"
    )

    data = response.json()

    user_id = data.get("id")

    logger.info(
        f"[{correlation_id}] Resolved User ID: {user_id}"
    )

    if not user_id:
        raise GraphClientError(
            "Unable to resolve recipient user.",
            404,
        )

    return user_id


# ------------------------------------------------------------------
# Create Chat
# ------------------------------------------------------------------

async def _create_chat(
    *,
    recipient_user_id: str,
    correlation_id: str,
) -> str:
    """
    Creates a one-to-one Teams chat.
    """

    logger.info(
        f"[{correlation_id}] STEP 2 - Creating Teams chat."
    )

    payload = {
        "chatType": "oneOnOne",
        "members": [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"{GRAPH_BASE_URL}/users('{recipient_user_id}')",
            }
        ],
    }

    logger.info(
        f"[{correlation_id}] Calling POST {GRAPH_CHATS_ENDPOINT}"
    )

    response = await graph_client.post(
        endpoint=GRAPH_CHATS_ENDPOINT,
        payload=payload,
        tenant_id=TENANT_ID,
        correlation_id=correlation_id,
    )

    logger.info(
        f"[{correlation_id}] Chat creation returned HTTP {response.status_code}"
    )

    data = response.json()

    chat_id = data.get("id")

    logger.info(
        f"[{correlation_id}] Chat ID: {chat_id}"
    )

    if not chat_id:
        raise GraphClientError(
            "Unable to create Teams chat.",
            500,
        )

    return chat_id


# ------------------------------------------------------------------
# Send Message
# ------------------------------------------------------------------

async def _send_chat_message(
    *,
    chat_id: str,
    request: SendTeamsMessageRequest,
    correlation_id: str,
):
    """
    Sends a Teams message to an existing chat.
    """

    logger.info(
        f"[{correlation_id}] STEP 3 - Sending Teams message."
    )

    payload = build_send_teams_message_payload(request)

    endpoint = GRAPH_CHAT_MESSAGES_ENDPOINT.format(
        chat_id=chat_id,
    )

    logger.info(
        f"[{correlation_id}] Calling POST {endpoint}"
    )

    response = await graph_client.post(
        endpoint=endpoint,
        payload=payload,
        tenant_id=TENANT_ID,
        correlation_id=correlation_id,
    )

    logger.info(
        f"[{correlation_id}] Message send returned HTTP {response.status_code}"
    )

    return response


# ------------------------------------------------------------------
# Main Orchestrator
# ------------------------------------------------------------------

async def send_teams_message(
    request: SendTeamsMessageRequest,
    correlation_id: str,
) -> SendTeamsMessageResponse:
    """
    End-to-end Teams message workflow.
    """

    logger.info(
        f"[{correlation_id}] Teams message workflow started."
    )

    try:

        recipient_user_id = await _get_user_id(
            recipient=request.recipient,
            correlation_id=correlation_id,
        )

        chat_id = await _create_chat(
            recipient_user_id=recipient_user_id,
            correlation_id=correlation_id,
        )

        response = await _send_chat_message(
            chat_id=chat_id,
            request=request,
            correlation_id=correlation_id,
        )

        logger.info(
            f"[{correlation_id}] Teams workflow completed successfully."
        )

        return parse_send_teams_message_success(
            status_code=response.status_code,
            request_id=correlation_id,
        )

    except GraphClientError as ex:

        logger.exception(
            f"[{correlation_id}] GraphClientError | Status={ex.status_code} | Message={ex.message}"
        )

        return parse_send_teams_message_error(
            status_code=ex.status_code,
            request_id=correlation_id,
            message=ex.message,
            retryable=ex.status_code >= 500,
        )

    except Exception as ex:

        logger.exception(
            f"[{correlation_id}] Unexpected exception: {str(ex)}"
        )

        return parse_send_teams_message_error(
            status_code=500,
            request_id=correlation_id,
            message=str(ex),
            retryable=False,
        )