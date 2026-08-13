# backend/tools/teams/builder.py

from tools.teams.models import SendTeamsMessageRequest


def build_send_teams_message_payload(
    request: SendTeamsMessageRequest,
) -> dict:
    """
    Builds the exact Microsoft Graph payload required
    to send a Teams chat message.

    This is the only place that knows Graph's JSON
    request structure.
    """

    return {
        "body": {
            "contentType": "text",
            "content": request.message,
        }
    }