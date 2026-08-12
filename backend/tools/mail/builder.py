# backend/tools/mail/builder.py
from core.constants import SYSTEM_MAILBOX
from core.enums import Importance
from tools.mail.models import SendMailRequest


def build_send_mail_payload(request: SendMailRequest) -> dict:
    importance_map = {
        Importance.LOW: "low",
        Importance.NORMAL: "normal",
        Importance.HIGH: "high",
    }

    return {
        "message": {
            "subject": request.subject,
            "body": {
                "contentType": "HTML",  # was "Text" — now accepts HTML markup
                "content": request.body,
            },
            "toRecipients": [{"emailAddress": {"address": request.recipient}}],
            "importance": importance_map[request.importance],
        },
        "saveToSentItems": request.save_to_sent_items,
    }