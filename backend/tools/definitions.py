# backend/tools/definitions.py
from core.enums import ToolName
from tools.mail.tool import execute_send_mail, send_mail

# Maps tool name -> internal business-logic callable.
# Used by the dispatcher for routing/logging.
TOOL_REGISTRY = {
    ToolName.SEND_MAIL.value: execute_send_mail,
}

# List of @ai_function-decorated callables passed directly to ChatAgent.
# Agent Framework auto-generates each tool's JSON schema from the
# function's type hints (including enums) — no manual schema needed.
ALL_TOOLS = [send_mail]