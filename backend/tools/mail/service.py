# backend/tools/mail/service.py
from clients.graph_client import graph_client, GraphClientError
from core.constants import GRAPH_SEND_MAIL_ENDPOINT, TENANT_ID
from tools.mail.builder import build_send_mail_payload
from tools.mail.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    ResourceNotFoundError,
    GraphServiceError,
    MailToolError,
)
from tools.mail.models import SendMailRequest, SendMailResponse
from tools.mail.parser import parse_send_mail_success
from utils.logger import get_logger

logger = get_logger(__name__)


async def send_mail(request: SendMailRequest, correlation_id: str) -> SendMailResponse:
    """
    Business logic layer. Uses the fixed TENANT_ID from constants
    instead of a per-request company lookup — single-tenant setup.
    """
    payload = build_send_mail_payload(request)
    endpoint = GRAPH_SEND_MAIL_ENDPOINT.format(mailbox=request.mailbox)

    try:
        response = await graph_client.post(
            endpoint=endpoint,
            payload=payload,
            tenant_id=TENANT_ID,
            correlation_id=correlation_id,
        )
    except GraphClientError as e:
        logger.error(f"[{correlation_id}] Graph error {e.status_code}: {e.message}")
        raise _translate_graph_error(e, request.mailbox)
    except Exception as e:
        logger.exception(f"[{correlation_id}] Unexpected error calling Graph.")
        raise GraphServiceError(f"Unexpected error sending mail: {str(e)}")

    result = parse_send_mail_success(response, correlation_id)
    return SendMailResponse(**result)


def _translate_graph_error(error: "GraphClientError", mailbox: str) -> MailToolError:
    if error.status_code == 401:
        return AuthenticationError()
    if error.status_code == 403:
        return PermissionDeniedError()
    if error.status_code == 404:
        return ResourceNotFoundError(mailbox)
    return GraphServiceError(error.message, status_code=error.status_code)