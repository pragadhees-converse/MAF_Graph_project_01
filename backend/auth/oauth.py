# backend/auth/oauth.py
import msal

from core.settings import get_settings

# Delegated scopes: User.Read for identity, User.ReadBasic.All to resolve
# other org members by email, Chat.Create + Chat.ReadWrite to create/post
# to 1:1 Teams chats as the logged-in user.
LOGIN_SCOPES = ["User.Read", "User.ReadBasic.All", "Chat.Create", "Chat.ReadWrite"]


def _build_msal_app(cache: msal.SerializableTokenCache | None = None) -> msal.ConfidentialClientApplication:
    settings = get_settings()
    authority = f"https://login.microsoftonline.com/{settings.AZURE_AD_TENANT_ID}"
    return msal.ConfidentialClientApplication(
        client_id=settings.AZURE_AD_CLIENT_ID,
        client_credential=settings.AZURE_AD_CLIENT_SECRET,
        authority=authority,
        token_cache=cache,
    )


def build_auth_code_flow() -> dict:
    settings = get_settings()
    app = _build_msal_app()
    return app.initiate_auth_code_flow(
        LOGIN_SCOPES, redirect_uri=settings.AZURE_AD_REDIRECT_URI
    )


def complete_auth_code_flow(flow: dict, auth_response: dict, cache: msal.SerializableTokenCache) -> dict:
    """
    Exchanges the code for tokens. The cache passed in captures the
    access token, refresh token, and account info — caller is
    responsible for serializing and storing `cache` after this call
    (see router/auth.py), since that's what makes future Teams calls
    possible without asking the user to log in again.
    """
    app = _build_msal_app(cache)
    return app.acquire_token_by_auth_code_flow(flow, auth_response, scopes=LOGIN_SCOPES)