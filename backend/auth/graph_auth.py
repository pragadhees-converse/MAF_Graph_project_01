# backend/auth/graph_auth.py
import msal

from core.constants import GRAPH_SCOPE
from core.settings import get_settings


class GraphAuthError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def build_msal_app(tenant_id: str) -> msal.ConfidentialClientApplication:
    """
    Creates an MSAL confidential client app scoped to a tenant.
    A fresh instance is built whenever a forced refresh is needed
    (see TokenManager.force_refresh), since discarding the app
    instance is how we bypass MSAL's own internal token cache.
    """
    settings = get_settings()
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    return msal.ConfidentialClientApplication(
        client_id=settings.AZURE_AD_CLIENT_ID,
        client_credential=settings.AZURE_AD_CLIENT_SECRET,
        authority=authority,
    )


def acquire_token(app: msal.ConfidentialClientApplication) -> dict:
    """
    Client credentials flow via MSAL. MSAL checks its own internal
    cache first and only hits Azure AD over the network if no valid
    cached token exists for this scope.
    """
    result = app.acquire_token_for_client(scopes=[GRAPH_SCOPE])

    if "access_token" not in result:
        raise GraphAuthError(
            result.get("error_description", "Failed to acquire Graph token."),
            status_code=result.get("status_code"),
        )

    return result