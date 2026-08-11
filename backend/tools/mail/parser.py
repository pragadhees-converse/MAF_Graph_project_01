# backend/tools/mail/parser.py
import httpx

from utils.response import success_response, error_response


def parse_send_mail_success(response: httpx.Response, request_id: str) -> dict:
    """
    Converts a successful Graph response into the standardized
    application response. Graph's sendMail returns 202 Accepted
    with an empty body on success — we never forward raw Graph
    output to the LLM, just this normalized shape.
    """
    return success_response(
        message="Email sent successfully.",
        status_code=response.status_code,
        request_id=request_id,
    )


def parse_send_mail_error(message: str, status_code: int, request_id: str, retryable: bool = False) -> dict:
    return error_response(
        message=message,
        status_code=status_code,
        request_id=request_id,
        retryable=retryable,
    )