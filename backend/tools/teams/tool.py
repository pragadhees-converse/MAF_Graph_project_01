import json
from typing import Annotated

from pydantic import Field
from agent_framework import tool

from core.enums import ToolName

from tools.teams.models import (
    SendTeamsMessageRequest,
)

from tools.teams.validator import (
    validate_send_teams_message_request,
)

from tools.teams.service import (
    send_teams_message,
)

from tools.teams.errors import (
    TeamsToolError,
)

from utils.correlation import generate_correlation_id
from utils.logger import get_logger

logger = get_logger(__name__)


#Internal Function

async def execute_send_teams_message(
    raw_args: dict,
    logged_in_user_email: str,
):
    """
    Internal Teams implementation.
    Called only by the dispatcher.
    """

    correlation_id = generate_correlation_id()

    logger.info(
        f"[{correlation_id}] Teams tool execution started."
    )

    try:

        request = SendTeamsMessageRequest(
            **raw_args,
        )

        validate_send_teams_message_request(
            request=request,
            logged_in_user_email=logged_in_user_email,
        )

        return await send_teams_message(
            request=request,
            correlation_id=correlation_id,
        )

    except TeamsToolError as ex:

        logger.exception(
            f"[{correlation_id}] Teams tool failed."
        )

        from tools.teams.parser import (
            parse_send_teams_message_error,
        )

        return parse_send_teams_message_error(
            status_code=ex.status_code,
            request_id=correlation_id,
            message=ex.message,
            retryable=ex.retryable,
        )

    except Exception as ex:

        logger.exception(
            f"[{correlation_id}] Unexpected Teams tool failure."
        )

        from tools.teams.parser import (
            parse_send_teams_message_error,
        )

        return parse_send_teams_message_error(
            status_code=500,
            request_id=correlation_id,
            message=str(ex),
            retryable=False,
        )


#LLM Tool

def make_teams_tools(
    logged_in_user_email: str,
) -> list:
    """
    Builds the Teams tools for one logged-in user.
    """

    @tool(
        name=ToolName.SEND_TEAMS_MESSAGE.value,
        description=(
            "Send a Microsoft Teams message "
            "to the currently logged-in user."
        ),
    )
    async def send_teams_message_tool(
        message: Annotated[
            str,
            Field(
                description="Teams message content.",
                min_length=1,
            ),
        ],
    ) -> str:
        """
        Tool visible to the LLM.
        """

        result = await execute_send_teams_message(
            raw_args={
                "recipient": logged_in_user_email,
                "message": message,
            },
            logged_in_user_email=logged_in_user_email,
        )

        return json.dumps(result.model_dump())

    return [send_teams_message_tool]

