# backend/auth/token_manager.py
import time
import asyncio

import msal

from auth.graph_auth import build_msal_app, acquire_token


class TokenManager:
    """
    Caches access tokens per tenant_id and refreshes automatically
    before expiry. Wraps MSAL, but keeps our own explicit expiry
    tracking so we have precise control over force-refresh on 401.
    """

    def __init__(self, expiry_buffer_seconds: int = 60):
        self._apps: dict[str, msal.ConfidentialClientApplication] = {}
        self._cache: dict[str, dict] = {}
        self._lock = asyncio.Lock()
        self._expiry_buffer_seconds = expiry_buffer_seconds

    async def get_token(self, tenant_id: str) -> str:
        cached = self._cache.get(tenant_id)
        if cached and cached["expires_at"] > time.time():
            return cached["access_token"]
        return await self._refresh_token(tenant_id)

    async def force_refresh(self, tenant_id: str) -> str:
        """Called by graph_client on a 401 — discard cache and MSAL app."""
        async with self._lock:
            self._apps.pop(tenant_id, None)
            self._cache.pop(tenant_id, None)
        return await self._refresh_token(tenant_id)

    async def _refresh_token(self, tenant_id: str) -> str:
        async with self._lock:
            cached = self._cache.get(tenant_id)
            if cached and cached["expires_at"] > time.time():
                return cached["access_token"]

            app = self._apps.get(tenant_id)
            if app is None:
                app = build_msal_app(tenant_id)
                self._apps[tenant_id] = app

            # MSAL's call is a blocking network request — offload it
            # so the event loop isn't blocked.
            token_data = await asyncio.to_thread(acquire_token, app)

            access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            expires_at = time.time() + expires_in - self._expiry_buffer_seconds

            self._cache[tenant_id] = {
                "access_token": access_token,
                "expires_at": expires_at,
            }
            return access_token


# Singleton shared across the app
token_manager = TokenManager()