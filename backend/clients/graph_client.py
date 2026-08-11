# backend/clients/graph_client.py
import httpx

from auth.token_manager import token_manager
from core.constants import (
    GRAPH_BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
    SUCCESS_STATUS_CODES,
    RETRYABLE_STATUS_CODES,
)
from utils.retry import call_with_retry, RetryExhaustedError
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphClientError(Exception):
    """Raised for non-retryable, non-auth Graph HTTP errors (e.g. 400, 404)."""

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class GraphClient:
    """
    Generic, tool-agnostic HTTP client for Microsoft Graph.

    Responsibilities:
    - Attaches Bearer token (via TokenManager, cached)
    - Attaches correlation ID header
    - Routes retryable failures (408/429/5xx) through utils.retry
    - Handles 401 -> force refresh token -> retry once
    - Raises typed errors for 403/404/400 so the service layer can
      translate them into MailToolError subclasses

    Tools/services NEVER call httpx directly — only through this client.
    """

    def __init__(self):
        self._base_url = GRAPH_BASE_URL
        self._timeout = DEFAULT_TIMEOUT_SECONDS

    async def post(
        self,
        endpoint: str,
        payload: dict,
        tenant_id: str,
        correlation_id: str,
    ) -> httpx.Response:
        return await self._request(
            method="POST",
            endpoint=endpoint,
            payload=payload,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )

    async def get(
        self,
        endpoint: str,
        tenant_id: str,
        correlation_id: str,
    ) -> httpx.Response:
        return await self._request(
            method="GET",
            endpoint=endpoint,
            payload=None,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )

    async def _request(
        self,
        method: str,
        endpoint: str,
        payload: dict | None,
        tenant_id: str,
        correlation_id: str,
        _is_retry_after_401: bool = False,
    ) -> httpx.Response:
        url = f"{self._base_url}{endpoint}"
        access_token = await token_manager.get_token(tenant_id)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "client-request-id": correlation_id,
        }

        async def do_call() -> httpx.Response:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                return await client.request(
                    method=method, url=url, json=payload, headers=headers
                )

        def get_status(response: httpx.Response) -> int:
            return response.status_code

        try:
            response = await call_with_retry(do_call, get_status)
        except RetryExhaustedError as e:
            logger.error(f"[{correlation_id}] Retry exhausted calling Graph: {e.message}")
            raise

        status_code = response.status_code

        # --- 401: refresh token once and retry, but only once ---
        if status_code == 401 and not _is_retry_after_401:
            logger.warning(f"[{correlation_id}] 401 received. Forcing token refresh.")
            await token_manager.force_refresh(tenant_id)
            return await self._request(
                method, endpoint, payload, tenant_id, correlation_id,
                _is_retry_after_401=True,
            )

        if status_code == 401 and _is_retry_after_401:
            logger.error(f"[{correlation_id}] 401 persisted after token refresh.")
            raise GraphClientError("Authentication failed after token refresh.", 401)

        if status_code == 403:
            raise GraphClientError("Permission denied by Microsoft Graph.", 403)

        if status_code == 404:
            raise GraphClientError("Requested Graph resource not found.", 404)

        if status_code == 400:
            raise GraphClientError(f"Graph rejected the request: {response.text}", 400)

        if status_code in RETRYABLE_STATUS_CODES:
            # Reached here only if retries were exhausted above and
            # call_with_retry returned the last response instead of raising
            # (shouldn't normally happen, but guarded for safety)
            raise GraphClientError(f"Graph returned retryable error: {status_code}", status_code)

        if status_code not in SUCCESS_STATUS_CODES:
            raise GraphClientError(f"Unexpected Graph status code: {status_code}", status_code)

        return response


# Singleton shared across the app
graph_client = GraphClient()