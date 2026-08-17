# backend/tools/teams/exceptions.py

class TeamsToolError(Exception):
    def __init__(self, message: str, status_code: int = 400, retryable: bool = False):
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        super().__init__(message)


class ValidationError(TeamsToolError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400, retryable=False)


class AuthenticationError(TeamsToolError):
    def __init__(self, message: str = "Authentication with Graph failed."):
        super().__init__(message, status_code=401, retryable=False)


class PermissionDeniedError(TeamsToolError):
    def __init__(self, message: str = "Permission denied by Microsoft Graph."):
        super().__init__(message, status_code=403, retryable=False)


class ResourceNotFoundError(TeamsToolError):
    def __init__(self, user_id: str):
        super().__init__(f"User '{user_id}' not found.", status_code=404, retryable=False)


class GraphServiceError(TeamsToolError):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, status_code=status_code, retryable=True)