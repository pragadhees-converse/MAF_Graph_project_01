# backend/tools/mail/validator.py
from core.constants import MAILBOX_DOMAIN, SUBJECT_MAX_LENGTH, BODY_MAX_LENGTH
from tools.mail.exceptions import ValidationError
from tools.mail.models import SendMailRequest
from utils.logger import get_logger

logger = get_logger(__name__)


def validate_send_mail_request(request: SendMailRequest) -> None:
    """
    Validates business rules that Pydantic alone can't express.
    Since this is single-tenant/single-company for phase 1, this
    only checks mailbox domain and length limits — no company/
    tenant/environment lookup is needed anymore.
    """

    mailbox_domain = request.mailbox.split("@")[-1].lower()
    if mailbox_domain != MAILBOX_DOMAIN.lower():
        raise ValidationError(
            f"Mailbox domain '{mailbox_domain}' is not allowed. "
            f"Expected '{MAILBOX_DOMAIN}'."
        )

    if len(request.subject) > SUBJECT_MAX_LENGTH:
        raise ValidationError(
            f"Subject exceeds max length of {SUBJECT_MAX_LENGTH} characters."
        )

    if len(request.body) > BODY_MAX_LENGTH:
        raise ValidationError(
            f"Body exceeds max length of {BODY_MAX_LENGTH} characters."
        )

    if request.recipient.lower() == request.mailbox.lower():
        raise ValidationError("Recipient cannot be the same as the sender mailbox.")