# backend/clients/graph_client.py

import httpx

from auth.token_manager import token_manager

from core.constants import (
    GRAPH_BASE_URL,
    DEFAULT_TIMEOUT_SECONDS,
    SUCCESS_STATUS_CODES,
    RETRYABLE_STATUS_CODES,
)

from utils.retry import (
    call_with_retry,
    RetryExhaustedError,
)

from utils.logger import get_logger

logger = get_logger(__name__)


class GraphClientError(Exception):
    """
    Raised when Microsoft Graph returns
    a non-success response.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class GraphClient:
    """
    Generic Microsoft Graph HTTP client.

    Responsibilities

    • Attach OAuth access token (app-only, cached via token_manager,
      OR delegated, passed in explicitly by the caller)
    • Token refresh on 401 — app-only calls only (see note below)
    • Retry transient failures
    • Correlation ID propagation
    • Centralized HTTP handling

    This client stays identity-agnostic on purpose: it doesn't know
    about tenants, users, or delegated auth internals — it just uses
    whatever token it's given, or fetches an app-only one if none is
    given. Delegated token acquisition/refresh lives in
    auth/delegated_auth.py, one layer above this.
    """

    def __init__(self):
        self._base_url = GRAPH_BASE_URL
        self._timeout = DEFAULT_TIMEOUT_SECONDS

    #################################################################
    # Public APIs
    #################################################################

    async def get(
        self,
        *,
        endpoint: str,
        tenant_id: str | None = None,
        correlation_id: str,
        access_token: str | None = None,
    ) -> httpx.Response:

        return await self._request(
            method="GET",
            endpoint=endpoint,
            payload=None,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            access_token=access_token,
        )

    async def post(
        self,
        *,
        endpoint: str,
        payload: dict,
        tenant_id: str | None = None,
        correlation_id: str,
        access_token: str | None = None,
    ) -> httpx.Response:

        return await self._request(
            method="POST",
            endpoint=endpoint,
            payload=payload,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            access_token=access_token,
        )

    async def patch(
        self,
        *,
        endpoint: str,
        payload: dict,
        tenant_id: str | None = None,
        correlation_id: str,
        access_token: str | None = None,
    ) -> httpx.Response:

        return await self._request(
            method="PATCH",
            endpoint=endpoint,
            payload=payload,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            access_token=access_token,
        )

    async def delete(
        self,
        *,
        endpoint: str,
        tenant_id: str | None = None,
        correlation_id: str,
        access_token: str | None = None,
    ) -> httpx.Response:

        return await self._request(
            method="DELETE",
            endpoint=endpoint,
            payload=None,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            access_token=access_token,
        )

    #################################################################
    # Internal Request Handler
    #################################################################

    async def _request(
        self,
        *,
        method: str,
        endpoint: str,
        payload: dict | None,
        tenant_id: str | None,
        correlation_id: str,
        retry_after_refresh: bool = False,
        access_token: str | None = None,
    ) -> httpx.Response:

        logger.info(
            f"[{correlation_id}] Graph Request -> {method} {endpoint}"
        )

        # Delegated calls (Teams) pass access_token directly — already
        # fetched/refreshed via auth/delegated_auth.py before reaching
        # here. App-only calls (Mail) pass no token, so we fall back to
        # the cached tenant-wide token from token_manager.
        is_delegated_call = access_token is not None
        token = access_token or await token_manager.get_token(tenant_id)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "client-request-id": correlation_id,
        }

        url = f"{self._base_url}{endpoint}"

        async def do_call():

            async with httpx.AsyncClient(
                timeout=self._timeout,
            ) as client:

                return await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=payload,
                )

        def status(response: httpx.Response):
            return response.status_code

        try:

            response = await call_with_retry(
                do_call,
                status,
            )

        except RetryExhaustedError:

            logger.exception(
                f"[{correlation_id}] Retry exhausted calling Graph."
            )
            raise

        status_code = response.status_code

        logger.info(
            f"[{correlation_id}] Graph Response <- HTTP {status_code}"
        )

        ##########################################################
        # Authentication
        ##########################################################

        if status_code == 401:

            logger.error(
                f"[{correlation_id}] Graph Response Body: {response.text}"
            )

            if retry_after_refresh:

                raise GraphClientError(
                    "Authentication failed after token refresh.",
                    401,
                )

            if is_delegated_call:
                # KNOWN GAP: delegated tokens are refreshed proactively
                # in auth/delegated_auth.py before the call is made, but
                # this client has no way to trigger a mid-request refresh
                # for a delegated token — it doesn't know which user the
                # token belongs to. A 401 here means the token was
                # rejected despite looking valid (revoked, conditional
                # access change, clock skew) — surfaces immediately as
                # an error rather than retrying. tools/teams/service.py
                # maps this to AuthenticationError, which tells the user
                # to log in again.
                logger.error(
                    f"[{correlation_id}] Delegated token rejected with 401 — "
                    "no automatic retry available for delegated calls."
                )
                raise GraphClientError(
                    "Authentication failed for delegated request.",
                    401,
                )

            logger.warning(
                f"[{correlation_id}] Refreshing expired token."
            )

            await token_manager.force_refresh(tenant_id)

            return await self._request(
                method=method,
                endpoint=endpoint,
                payload=payload,
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                retry_after_refresh=True,
            )

        ##########################################################
        # Authorization
        ##########################################################

        if status_code == 403:

            logger.error(
                f"[{correlation_id}] Graph Response Body: {response.text}"
            )

            raise GraphClientError(
                response.text,
                403,
            )

        ##########################################################
        # Resource not found
        ##########################################################

        if status_code == 404:

            logger.error(
                f"[{correlation_id}] Graph Response Body: {response.text}"
            )

            raise GraphClientError(
                response.text,
                404,
            )

        ##########################################################
        # Invalid request
        ##########################################################

        if status_code == 400:

            logger.error(
                f"[{correlation_id}] Graph Response Body: {response.text}"
            )

            raise GraphClientError(
                response.text,
                400,
            )

        ##########################################################
        # Retryable Graph errors
        ##########################################################

        if status_code in RETRYABLE_STATUS_CODES:

            logger.error(
                f"[{correlation_id}] Graph Response Body: {response.text}"
            )

            raise GraphClientError(
                f"Retryable Graph error ({status_code})",
                status_code,
            )

        ##########################################################
        # Unknown error
        ##########################################################

        if status_code not in SUCCESS_STATUS_CODES:

            logger.error(
                f"[{correlation_id}] Graph Response Body: {response.text}"
            )

            raise GraphClientError(
                f"Unexpected Graph status ({status_code})",
                status_code,
            )

        logger.info(
            f"[{correlation_id}] Graph call completed successfully."
        )

        return response


graph_client = GraphClient()