# backend/utils/adaptive_card.py
"""
Builds Adaptive Card JSON payloads used by Teams messages, and a
matching card-styled HTML layout used for Mail (since true interactive
Adaptive Cards in Outlook require Actionable Message provider
registration with Microsoft — a manual approval process, not
something achievable purely in code).
"""


def build_teams_adaptive_card(title: str, body_html: str) -> dict:
    """
    Real, interactive Adaptive Card for Teams. body_html is expected
    to already be safe HTML (from utils.html_format.ensure_html_body),
    rendered here as a TextBlock with isSubtle formatting preserved
    via simple tag stripping — Adaptive Cards use their own markdown-
    lite syntax, not raw HTML, inside TextBlock.
    """
    import re

    # Adaptive Card TextBlocks support a small markdown subset, not
    # HTML — strip tags to plain text with basic markdown re-added.
    plain = re.sub(r"<h[1-6]>(.*?)</h[1-6]>", r"**\1**\n", body_html)
    plain = re.sub(r"<li>(.*?)</li>", r"- \1", plain)
    plain = re.sub(r"<b>(.*?)</b>", r"**\1**", plain)
    plain = re.sub(r"<[^>]+>", "", plain).strip()

    return {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "text": title,
                "weight": "Bolder",
                "size": "Medium",
                "wrap": True,
            },
            {
                "type": "TextBlock",
                "text": plain,
                "wrap": True,
                "spacing": "Medium",
            },
        ],
    }


def build_mail_card_html(subject: str, body_html: str, sender_label: str = "Notification") -> str:
    """
    Card-styled HTML wrapper for Mail. Visually resembles a card
    (header banner, content section, footer) but has no interactive
    elements — this is the honest limitation for Mail without
    Actionable Message provider registration.
    """
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