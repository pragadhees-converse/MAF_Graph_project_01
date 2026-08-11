# backend/dispatcher/tool_dispatcher.py
from utils.correlation import generate_correlation_id
from utils.logger import get_logger
from utils.response import error_response

logger = get_logger(__name__)


class ToolDispatcher:
    """
    Routes a tool call (by name) to its registered implementation.

    Responsibilities:
    - Confirm the tool exists in TOOL_REGISTRY
    - Invoke it with the raw arguments
    - Return a standardized dict response in all cases, including
      unknown tool names or unexpected dispatch-level failures

    No Graph logic, no validation logic, no business logic lives
    here — purely a routing layer.

    NOTE: TOOL_REGISTRY is imported lazily inside dispatch() rather
    than at module load time. tools/definitions.py imports
    tools/mail/tool.py, which imports this dispatcher module — so
    importing TOOL_REGISTRY at the top of this file creates a
    circular import. Deferring the import until dispatch() is first
    called breaks the cycle, since by then every module involved has
    already finished loading.
    """

    def __init__(self):
        self._registry = None

    def _get_registry(self) -> dict:
        if self._registry is None:
            from tools.definitions import TOOL_REGISTRY
            self._registry = TOOL_REGISTRY
        return self._registry

    async def dispatch(self, tool_name: str, raw_args: dict) -> dict:
        correlation_id = generate_correlation_id()
        registry = self._get_registry()

        tool_fn = registry.get(tool_name)

        if tool_fn is None:
            logger.warning(f"[{correlation_id}] Unknown tool requested: '{tool_name}'")
            return error_response(
                message=f"Unknown tool: '{tool_name}'.",
                status_code=400,
                request_id=correlation_id,
                retryable=False,
            )

        try:
            logger.info(f"[{correlation_id}] Dispatching tool '{tool_name}'")
            return await tool_fn(raw_args)

        except Exception:
            logger.exception(f"[{correlation_id}] Dispatcher-level failure for '{tool_name}'")
            return error_response(
                message="Internal error while dispatching tool.",
                status_code=500,
                request_id=correlation_id,
                retryable=True,
            )


# Singleton shared across the app
tool_dispatcher = ToolDispatcher()