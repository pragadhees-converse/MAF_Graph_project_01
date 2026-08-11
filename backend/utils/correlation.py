# backend/utils/correlation.py
import uuid


def generate_correlation_id() -> str:
    """
    Unique ID per request, used for tracing a request across
    logs, Graph calls, and retries. Sent as a header to Graph
    and included in every response for observability.
    """
    return str(uuid.uuid4())