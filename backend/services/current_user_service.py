# backend/services/current_user_service.py

from schemas.current_user import CurrentUser
from clients.graph_client import GraphClientError
from utils.logger import get_logger

import httpx

logger = get_logger(__name__)


GRAPH_ME_ENDPOINT = "https://graph.microsoft.com/v1.0/me"


class CurrentUserService:
    """
    Resolves the authenticated Microsoft user from a
    delegated Microsoft Graph access token.

    This is called once per authenticated request.

    Flow

        Access Token
             │
             ▼
        GET /me
             │
             ▼
        CurrentUser
    """

    async def get_current_user(
        self,
        access_token: str,
    ) -> CurrentUser:

        logger.info("Resolving authenticated Microsoft user.")

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient(timeout=15) as client:

            response = await client.get(
                GRAPH_ME_ENDPOINT,
                headers=headers,
            )

        if response.status_code != 200:

            logger.error(
                f"Failed to resolve current user. "
                f"Status={response.status_code}"
            )

            raise GraphClientError(
                message="Unable to resolve authenticated Microsoft user.",
                status_code=response.status_code,
            )

        data = response.json()

        logger.info(
            f"Authenticated user resolved: {data.get('displayName')}"
        )

        return CurrentUser(
            id=data["id"],
            display_name=data["displayName"],
            email=data.get("mail") or data.get("userPrincipalName"),
            access_token=access_token,
        )


current_user_service = CurrentUserService()