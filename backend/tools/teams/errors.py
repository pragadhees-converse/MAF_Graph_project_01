# backend/tools/teams/errors.py

class TeamsToolError(Exception):
    """
    Base exception for all Teams tool errors.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        retryable: bool = False,
    ):
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        super().__init__(message)


class TeamsValidationError(TeamsToolError):
    """
    Raised when the Teams request violates business rules.
    """

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            retryable=False,
        )


class TeamsAuthenticationError(TeamsToolError):
    """
    Raised when Microsoft Graph authentication fails.
    """

    def __init__(self, message: str = "Authentication failed."):
        super().__init__(
            message=message,
            status_code=401,
            retryable=True,
        )


class TeamsPermissionDeniedError(TeamsToolError):
    """
    Raised when the application does not have permission
    to perform the requested Teams operation.
    """

    def __init__(self, message: str = "Permission denied."):
        super().__init__(
            message=message,
            status_code=403,
            retryable=False,
        )


class TeamsResourceNotFoundError(TeamsToolError):
    """
    Raised when a Teams user, chat, or resource cannot be found.
    """

    def __init__(self, message: str = "Requested Teams resource not found."):
        super().__init__(
            message=message,
            status_code=404,
            retryable=False,
        )


class TeamsServiceUnavailableError(TeamsToolError):
    """
    Raised when Microsoft Graph is temporarily unavailable.
    """

    def __init__(self, message: str = "Microsoft Teams service unavailable."):
        super().__init__(
            message=message,
            status_code=503,
            retryable=True,
        )