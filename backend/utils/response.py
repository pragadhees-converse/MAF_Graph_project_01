# backend/utils/response.py

def success_response(
    message: str,
    status_code: int,
    request_id: str,
) -> dict:
    return {
        "success": True,
        "status_code": status_code,
        "message": message,
        "request_id": request_id,
        "retryable": False,
    }


def error_response(
    message: str,
    status_code: int,
    request_id: str,
    retryable: bool = False,
) -> dict:
    return {
        "success": False,
        "status_code": status_code,
        "message": message,
        "request_id": request_id,
        "retryable": retryable,
    }