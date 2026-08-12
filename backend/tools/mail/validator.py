# backend/tools/mail/validator.py
from core.constants import SUBJECT_MAX_LENGTH, BODY_MAX_LENGTH
from tools.mail.exceptions import ValidationError
from tools.mail.models import SendMailRequest
from utils.logger import get_logger

logger = get_logger(__name__)


def validate_send_mail_request(request: SendMailRequest, logged_in_user_email: str) -> None:
    """
    The core rule for this system: the system can ONLY email the
    person currently logged in. It can never send to anyone else,
    regardless of what the LLM or user asks for. This is enforced
    here, not left to the LLM to "decide" correctly.
    """
    if request.recipient.lower() != logged_in_user_email.lower():
        raise ValidationError(
            "This system can only send mail to your own logged-in email address."
        )

    if len(request.subject) > SUBJECT_MAX_LENGTH:
        raise ValidationError(f"Subject exceeds max length of {SUBJECT_MAX_LENGTH} characters.")

    if len(request.body) > BODY_MAX_LENGTH:
        raise ValidationError(f"Body exceeds max length of {BODY_MAX_LENGTH} characters.")