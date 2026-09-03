# backend/utils/adaptive_card.py
import re


def build_teams_adaptive_card(
    title: str,
    body_html: str,
    approve_url: str | None = None,
    decline_url: str | None = None,
) -> dict:
    """
    Adaptive Card for Teams. If approve_url/decline_url are provided,
    the card includes real Action.OpenUrl buttons — clicking them opens
    a browser tab that hits our own backend and performs the action.
    This works without any Bot Framework registration, unlike
    Action.Submit, which requires a registered bot with a messaging
    endpoint to receive the click.
    """
    plain = re.sub(r"<h[1-6]>(.*?)</h[1-6]>", r"**\1**\n", body_html)
    plain = re.sub(r"<li>(.*?)</li>", r"- \1", plain)
    plain = re.sub(r"<b>(.*?)</b>", r"**\1**", plain)
    plain = re.sub(r"<[^>]+>", "", plain).strip()

    card = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {"type": "TextBlock", "text": title, "weight": "Bolder", "size": "Medium", "wrap": True},
            {"type": "TextBlock", "text": plain, "wrap": True, "spacing": "Medium"},
        ],
    }

    if approve_url and decline_url:
        card["actions"] = [
            {"type": "Action.OpenUrl", "title": "Approve", "url": approve_url},
            {"type": "Action.OpenUrl", "title": "Decline", "url": decline_url},
        ]

    return card


def build_mail_card_html(subject: str, body_html: str, sender_label: str = "Notification") -> str:
    return f"""
    <div style="max-width:600px;margin:0 auto;font-family:Segoe UI,Arial,sans-serif;
                border:1px solid #e1e1e1;border-radius:8px;overflow:hidden;">
      <div style="background:#2564cf;color:white;padding:16px 20px;">
        <div style="font-size:12px;opacity:0.85;">{sender_label}</div>
        <div style="font-size:18px;font-weight:600;margin-top:4px;">{subject}</div>
      </div>
      <div style="padding:20px;color:#1a1a1a;line-height:1.5;">
        {body_html}
      </div>
      <div style="padding:12px 20px;background:#f4f5f7;font-size:12px;color:#777;">
        Sent via Microsoft Graph Assistant
      </div>
    </div>
    """