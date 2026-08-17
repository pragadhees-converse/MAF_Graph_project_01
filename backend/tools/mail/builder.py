# backend/tools/mail/builder.py
from core.enums import Importance
from tools.mail.models import SendMailRequest
from utils.html_format import ensure_html_body


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
                "contentType": "HTML",
                "content": ensure_html_body(request.body),  # ← guarantees safe rendering
            },
            "toRecipients": [{"emailAddress": {"address": request.recipient}}],
            "importance": importance_map[request.importance],
        },
        "saveToSentItems": request.save_to_sent_items,
    }