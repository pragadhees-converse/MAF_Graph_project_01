# backend/tools/teams/validator.py
from core.constants import TEAMS_MESSAGE_MAX_LENGTH
from tools.teams.exceptions import ValidationError
from tools.teams.models import SendTeamsMessageRequest


def validate_send_teams_message_request(request: SendTeamsMessageRequest) -> None:
    if len(request.message.strip()) == 0:
        raise ValidationError("Message cannot be empty.")
    if len(request.message) > TEAMS_MESSAGE_MAX_LENGTH:
        raise ValidationError(f"Message exceeds max length of {TEAMS_MESSAGE_MAX_LENGTH} characters.")