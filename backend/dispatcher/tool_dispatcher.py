# backend/dispatcher/tool_dispatcher.py
from utils.correlation import generate_correlation_id
from utils.logger import get_logger
from utils.response import error_response

logger = get_logger(__name__)


class ToolDispatcher:
    def __init__(self):
        self._registry = None

    def _get_registry(self) -> dict:
        if self._registry is None:
            from tools.definitions import TOOL_REGISTRY
            self._registry = TOOL_REGISTRY
        return self._registry

    async def dispatch(self, tool_name: str, raw_args: dict, logged_in_user_email: str) -> dict:
        correlation_id = generate_correlation_id()
        registry = self._get_registry()
        tool_fn = registry.get(tool_name)

        if tool_fn is None:
            logger.warning(f"[{correlation_id}] Unknown tool requested: '{tool_name}'")
            return error_response(message=f"Unknown tool: '{tool_name}'.", status_code=400, request_id=correlation_id)

        try:
            logger.info(f"[{correlation_id}] Dispatching tool '{tool_name}'")
            return await tool_fn(raw_args, logged_in_user_email)
        except Exception:
            logger.exception(f"[{correlation_id}] Dispatcher-level failure for '{tool_name}'")
            return error_response(
                message="Internal error while dispatching tool.",
                status_code=500, request_id=correlation_id, retryable=True,
            )


tool_dispatcher = ToolDispatcher()