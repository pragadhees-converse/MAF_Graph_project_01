# backend/tools/definitions.py
from core.enums import ToolName
from tools.mail.tool import execute_send_mail, make_mail_tools

TOOL_REGISTRY = {
    ToolName.SEND_MAIL.value: execute_send_mail,
}


def get_tools_for_user(logged_in_user_email: str) -> list:
    """Builds the tool list scoped to one user's session."""
    return make_mail_tools(logged_in_user_email)