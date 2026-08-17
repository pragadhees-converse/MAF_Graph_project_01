# backend/auth/delegated_auth.py
import msal

from auth.delegated_token_store import get_cache, save_cache
from auth.oauth import LOGIN_SCOPES, _build_msal_app
from utils.logger import get_logger

logger = get_logger(__name__)


class DelegatedAuthError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


async def get_delegated_token(user_email: str) -> str:
    """
    Returns a valid delegated access token for this user, refreshing
    silently via MSAL if the cached one has expired. Raises
    DelegatedAuthError if the user has never logged in with these
    scopes, or their session can no longer be refreshed (they need
    to log in again).
    """
    serialized = get_cache(user_email)
    if serialized is None:
        raise DelegatedAuthError("No delegated session found. Please log in again.")

    cache = msal.SerializableTokenCache()
    cache.deserialize(serialized)

    app = _build_msal_app(cache)
    accounts = app.get_accounts()
    if not accounts:
        raise DelegatedAuthError("Delegated session expired. Please log in again.")

    result = app.acquire_token_silent(LOGIN_SCOPES, account=accounts[0])

    # MSAL refreshes the token in-place inside `cache` if it was near
    # expiry — persist that back so the next call benefits from it too.
    if cache.has_state_changed:
        save_cache(user_email, cache.serialize())

    if not result or "access_token" not in result:
        raise DelegatedAuthError("Could not refresh delegated session. Please log in again.")

    return result["access_token"]