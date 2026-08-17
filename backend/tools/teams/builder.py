# backend/tools/teams/builder.py
from tools.teams.models import SendTeamsMessageRequest


def build_activity_notification_payload(request: SendTeamsMessageRequest) -> dict:
    """
    Builds the payload for Graph's sendActivityNotification endpoint.
    This is what shows up in the recipient's Teams activity feed.
    """
    return {
        "topic": {
            "source": "text",
            "value": "Assistant Notification",
        },
        "activityType": "systemDefault",
        "previewText": {
            "content": request.message[:150],
        },
        "templateParameters": [
            {"name": "systemUser", "value": "Assistant"},
        ],
    }