# backend/tools/mail/builder.py
from core.enums import Importance
from tools.mail.models import SendMailRequest


def build_send_mail_payload(request: SendMailRequest) -> dict:
    """
    Converts a validated SendMailRequest into the exact JSON body
    Microsoft Graph's /sendMail endpoint expects.

    This is the ONLY place Graph's payload shape is known. The LLM
    never sees this structure, and the service/client layers just
    pass this dict through untouched.
    """

    importance_map = {
        Importance.LOW: "low",
        Importance.NORMAL: "normal",
        Importance.HIGH: "high",
    }

    return {
        "message": {
            "subject": request.subject,
            "body": {
                "contentType": "Text",
                "content": request.body,
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": request.recipient
                    }
                }
            ],
            "importance": importance_map[request.importance],
        },
        "saveToSentItems": request.save_to_sent_items,
    }