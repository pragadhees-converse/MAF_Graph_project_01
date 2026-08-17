# backend/tools/mail/builder.py
from core.enums import Importance
from tools.mail.models import SendMailRequest
from utils.adaptive_card import build_mail_card_html
from utils.html_format import ensure_html_body


def build_send_mail_payload(request: SendMailRequest) -> dict:
    importance_map = {
        Importance.LOW: "low",
        Importance.NORMAL: "normal",
        Importance.HIGH: "high",
    }

    safe_body = ensure_html_body(request.body)
    card_html = build_mail_card_html(subject=request.subject, body_html=safe_body)

    return {
        "message": {
            "subject": request.subject,
            "body": {
                "contentType": "HTML",
                "content": card_html,
            },
            "toRecipients": [{"emailAddress": {"address": request.recipient}}],
            "importance": importance_map[request.importance],
        },
        "saveToSentItems": request.save_to_sent_items,
    }