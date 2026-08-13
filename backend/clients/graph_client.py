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

    • Attach OAuth access token
    • Token refresh on 401
    • Retry transient failures
    • Correlation ID propagation
    • Centralized HTTP handling
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

    async def post(
        self,
        *,
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

    async def patch(
        self,
        *,
        endpoint: str,
        payload: dict,
        tenant_id: str,
        correlation_id: str,
    ) -> httpx.Response:

        return await self._request(
            method="PATCH",
            endpoint=endpoint,
            payload=payload,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )

    async def delete(
        self,
        *,
        endpoint: str,
        tenant_id: str,
        correlation_id: str,
    ) -> httpx.Response:

        return await self._request(
            method="DELETE",
            endpoint=endpoint,
            payload=None,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
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
        tenant_id: str,
        correlation_id: str,
        retry_after_refresh: bool = False,
    ) -> httpx.Response:

        logger.info(
            f"[{correlation_id}] Graph Request -> {method} {endpoint}"
        )

        access_token = await token_manager.get_token(tenant_id)

        headers = {
            "Authorization": f"Bearer {access_token}",
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