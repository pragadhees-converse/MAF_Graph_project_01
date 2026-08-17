# backend/tools/mail/tool.py
import json
from typing import Annotated

from pydantic import Field
from agent_framework import tool

from core.enums import Importance, ToolName
from dispatcher.tool_dispatcher import tool_dispatcher
from tools.mail.draft_store import save_draft, get_draft, clear_draft
from tools.mail.exceptions import MailToolError
from tools.mail.models import SendMailRequest, SendMailResponse
from tools.mail.service import send_mail as send_mail_service
from tools.mail.validator import validate_send_mail_request
from utils.correlation import generate_correlation_id
from utils.logger import get_logger
from utils.response import error_response

logger = get_logger(__name__)


async def execute_send_mail(raw_args: dict, logged_in_user_email: str) -> dict:
    correlation_id = generate_correlation_id()

    try:
        request = SendMailRequest(**raw_args)
    except Exception as e:
        logger.warning(f"[{correlation_id}] Invalid send_mail arguments: {e}")
        return error_response(message=f"Invalid input: {str(e)}", status_code=400, request_id=correlation_id)

    try:
        validate_send_mail_request(request)
        result: SendMailResponse = await send_mail_service(request=request, correlation_id=correlation_id)
        return result.model_dump()

    except MailToolError as e:
        logger.error(f"[{correlation_id}] MailToolError: {e.message}")
        return error_response(message=e.message, status_code=e.status_code, request_id=correlation_id, retryable=e.retryable)

    except Exception:
        logger.exception(f"[{correlation_id}] Unhandled error in execute_send_mail.")
        return error_response(message="An unexpected error occurred while sending the email.", status_code=500, request_id=correlation_id, retryable=True)


def make_mail_tools(logged_in_user_email: str) -> list:

    @tool(
        name="draft_mail",
        description=(
            "Stage a draft email for review. This does NOT send the email — "
            "it only prepares it and shows it to the user for approval. "
            "Always use this first when asked to email something, and use it "
            "again only if the user wants to CHANGE the recipient, subject, "
            "or body — never call it again just to re-confirm an unchanged draft."
        ),
    )
    async def draft_mail(
        recipient: Annotated[str, Field(description="Recipient's email address. If the user says 'me'/'my inbox', use the logged-in user's own email.")],
        subject: Annotated[str, Field(description="Email subject line (max 150 characters).")],
        body: Annotated[str, Field(description="HTML content for the email body.")],
        importance: Annotated[Importance, Field(description="Email importance.")] = Importance.NORMAL,
        save_to_sent_items: Annotated[bool, Field(description="Save a copy in Sent Items.")] = True,
    ) -> str:
        draft = {
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "importance": importance,
            "save_to_sent_items": save_to_sent_items,
        }
        save_draft(logged_in_user_email, draft)
        logger.info(f"DRAFT CREATED | user={logged_in_user_email} | to={recipient} | subject='{subject}'")
        return json.dumps({
            "status": "draft_ready",
            "message": "Draft prepared. Show this to the user and ask them to approve or decline before calling confirm_send_mail.",
            "draft": draft,
        })

    @tool(
        name="confirm_send_mail",
        description=(
            "Send the previously staged draft, or discard it. Call this "
            "IMMEDIATELY when the user's message is an approval or decline "
            "of a draft you already showed — do not call draft_mail again first."
        ),
    )
    async def confirm_send_mail(
        approved: Annotated[bool, Field(description="True if approved, False if declined.")],
    ) -> str:
        draft = get_draft(logged_in_user_email)
        if draft is None:
            logger.warning(f"CONFIRM CALLED WITH NO PENDING DRAFT | user={logged_in_user_email}")
            return json.dumps({"status": "no_draft", "message": "There is no pending draft. Use draft_mail first."})

        clear_draft(logged_in_user_email)

        if not approved:
            logger.info(f"DRAFT DECLINED | user={logged_in_user_email} | subject='{draft['subject']}'")
            return json.dumps({"status": "declined", "message": "The email was not sent, as requested."})

        logger.info(f"DRAFT APPROVED, SENDING | user={logged_in_user_email} | to={draft['recipient']} | subject='{draft['subject']}'")
        result = await tool_dispatcher.dispatch(ToolName.SEND_MAIL.value, draft, logged_in_user_email)
        logger.info(f"SEND RESULT | user={logged_in_user_email} | {result}")
        return json.dumps(result)

    return [draft_mail, confirm_send_mail]