# backend/tools/mail/exceptions.py

class MailToolError(Exception):
    """Base exception for all mail tool errors."""

    def __init__(self, message: str, status_code: int = 400, retryable: bool = False):
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        super().__init__(message)


class ValidationError(MailToolError):
    """Raised when input validation fails (bad recipient, subject, domain, etc)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400, retryable=False)


class AuthenticationError(MailToolError):
    """Raised on unrecoverable 401 (after refresh + retry already attempted)."""

    def __init__(self, message: str = "Authentication with Graph failed."):
        super().__init__(message, status_code=401, retryable=False)


class PermissionDeniedError(MailToolError):
    """Raised on 403 — app lacks required Graph permissions/scope."""

    def __init__(self, message: str = "Permission denied by Microsoft Graph."):
        super().__init__(message, status_code=403, retryable=False)


class ResourceNotFoundError(MailToolError):
    """Raised on 404 — mailbox/user not found."""

    def __init__(self, mailbox: str):
        super().__init__(
            f"Mailbox '{mailbox}' not found.", status_code=404, retryable=False
        )


class GraphServiceError(MailToolError):
    """Raised on 5xx / retryable failures after retries are exhausted."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, status_code=status_code, retryable=True)