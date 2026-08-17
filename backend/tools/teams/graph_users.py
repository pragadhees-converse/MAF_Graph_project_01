# backend/tools/teams/graph_users.py
from clients.graph_client import graph_client
from core.constants import GRAPH_USER_BY_EMAIL_ENDPOINT


async def resolve_user_id(email: str, access_token: str, correlation_id: str) -> str:
    response = await graph_client.get(
        endpoint=GRAPH_USER_BY_EMAIL_ENDPOINT.format(user_principal_name=email),
        correlation_id=correlation_id,
        access_token=access_token,
    )
    return response.json()["id"]