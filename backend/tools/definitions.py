# backend/tools/definitions.py

from core.enums import ToolName

# -------------------------
# Mail
# -------------------------

from tools.mail.tool import (
    execute_send_mail,
    make_mail_tools,
)

# -------------------------
# Teams
# -------------------------

from tools.teams.tool import (
    execute_send_teams_message,
    make_teams_tools,
)


# ------------------------------------------------------------------
# Internal Tool Registry
#
# Used ONLY by ToolDispatcher.
# Maps a tool name -> internal execution function.
# ------------------------------------------------------------------

TOOL_REGISTRY = {
    ToolName.SEND_MAIL.value: execute_send_mail,
    ToolName.SEND_TEAMS_MESSAGE.value: execute_send_teams_message,
}


# ------------------------------------------------------------------
# Agent Tool Builder
#
# Builds the list of tools available to the logged-in user.
# These are the only functions exposed to the LLM.
# ------------------------------------------------------------------

def get_tools_for_user(
    logged_in_user_email: str,
) -> list:

    tools = []

    tools.extend(
        make_mail_tools(
            logged_in_user_email,
        )
    )

    tools.extend(
        make_teams_tools(
            logged_in_user_email,
        )
    )

    return tools