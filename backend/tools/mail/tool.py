# backend/tools/mail/tool.py
import json
from typing import Annotated

from pydantic import Field

from agent_framework import tool

from core.enums import Importance, ToolName
from dispatcher.tool_dispatcher import tool_dispatcher
from tools.mail.exceptions import MailToolError
from tools.mail.models import SendMailRequest, SendMailResponse
from tools.mail.service import send_mail as send_mail_service
from tools.mail.validator import validate_send_mail_request
from utils.correlation import generate_correlation_id
from utils.logger import get_logger
from utils.response import error_response

logger = get_logger(__name__)


async def execute_send_mail(raw_args: dict) -> dict:
    """Internal business entry point routed to by the dispatcher."""
    correlation_id = generate_correlation_id()

    try:
        request = SendMailRequest(**raw_args)
    except Exception as e:
        logger.warning(f"[{correlation_id}] Invalid send_mail arguments: {e}")
        return error_response(
            message=f"Invalid input: {str(e)}",
            status_code=400,
            request_id=correlation_id,
            retryable=False,
        )

    try:
        validate_send_mail_request(request)
        result: SendMailResponse = await send_mail_service(
            request=request,
            correlation_id=correlation_id,
        )
        return result.model_dump()

    except MailToolError as e:
        logger.error(f"[{correlation_id}] MailToolError: {e.message}")
        return error_response(
            message=e.message,
            status_code=e.status_code,
            request_id=correlation_id,
            retryable=e.retryable,
        )

    except Exception:
        logger.exception(f"[{correlation_id}] Unhandled error in execute_send_mail.")
        return error_response(
            message="An unexpected error occurred while sending the email.",
            status_code=500,
            request_id=correlation_id,
            retryable=True,
        )


@tool(
    name=ToolName.SEND_MAIL.value,
    description=(
        "Send an email on behalf of the configured mailbox via Microsoft Outlook. "
        "Use this when the user asks to send, draft-and-send, or email someone."
    ),
)
async def send_mail(
    mailbox: Annotated[str, Field(description="Sender mailbox email address.")],
    recipient: Annotated[str, Field(description="Recipient's email address.")],
    subject: Annotated[str, Field(description="Email subject line (max 150 characters).")],
    body: Annotated[str, Field(description="Plain text email body (max 20000 characters).")],
    importance: Annotated[
        Importance, Field(description="Email importance level.")
    ] = Importance.NORMAL,
    save_to_sent_items: Annotated[
        bool, Field(description="Whether to save a copy in Sent Items.")
    ] = True,
) -> str:
    """LLM-facing tool. No company_id/environment — single-tenant setup."""
    raw_args = {
        "mailbox": mailbox,
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "importance": importance,
        "save_to_sent_items": save_to_sent_items,
    }
    result = await tool_dispatcher.dispatch(ToolName.SEND_MAIL.value, raw_args)
    return json.dumps(result)