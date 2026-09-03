# backend/tools/teams/graph_users.py
from auth.token_manager import token_manager
from clients.graph_client import graph_client
from core.constants import GRAPH_USER_BY_EMAIL_ENDPOINT, TENANT_ID


async def resolve_user_id(email: str, access_token: str | None, correlation_id: str, use_app_only: bool = False) -> str:
    if use_app_only:
        response = await graph_client.get(
            endpoint=GRAPH_USER_BY_EMAIL_ENDPOINT.format(user_principal_name=email),
            tenant_id=TENANT_ID, correlation_id=correlation_id,
        )
    else:
        response = await graph_client.get(
            endpoint=GRAPH_USER_BY_EMAIL_ENDPOINT.format(user_principal_name=email),
            correlation_id=correlation_id, access_token=access_token,
        )
    return response.json()["id"]