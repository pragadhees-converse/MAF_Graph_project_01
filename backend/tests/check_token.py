import asyncio
import jwt

from auth.token_manager import token_manager
from core.constants import TENANT_ID


async def main():
    token = await token_manager.get_token(TENANT_ID)

    decoded = jwt.decode(
        token,
        options={"verify_signature": False},
    )

    print("\n========== GRAPH TOKEN ROLES ==========\n")

    for role in decoded.get("roles", []):
        print(role)

    print("\n=======================================\n")


asyncio.run(main())