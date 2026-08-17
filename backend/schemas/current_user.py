# backend/schemas/current_user.py

from pydantic import BaseModel, ConfigDict


class CurrentUser(BaseModel):
    """
    Authenticated Microsoft Entra ID user.

    Built once from the delegated Microsoft Graph token
    and passed throughout the application instead of
    repeatedly passing email or access token separately.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    display_name: str
    email: str
    access_token: str