# backend/tools/mail/validator.py
from core.constants import SUBJECT_MAX_LENGTH, BODY_MAX_LENGTH
from tools.mail.exceptions import ValidationError
from tools.mail.models import SendMailRequest


def validate_send_mail_request(request: SendMailRequest) -> None:
    if len(request.subject) > SUBJECT_MAX_LENGTH:
        raise ValidationError(f"Subject exceeds max length of {SUBJECT_MAX_LENGTH} characters.")
    if len(request.body) > BODY_MAX_LENGTH:
        raise ValidationError(f"Body exceeds max length of {BODY_MAX_LENGTH} characters.")