# backend/tools/teams/parser.py
import httpx
from utils.response import success_response


def parse_send_teams_message_success(response: httpx.Response, request_id: str) -> dict:
    # sendActivityNotification returns 201/204 with no body on success
    return success_response(
        message="Teams notification sent successfully.",
        status_code=response.status_code,
        request_id=request_id,
    )