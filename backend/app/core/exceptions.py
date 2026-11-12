from typing import Any


class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class NotFoundError(AppError):
    def __init__(
        self, message: str = "Resource not found", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, code="NOT_FOUND", status_code=404, details=details)


class ConflictError(AppError):
    def __init__(
        self, message: str = "Resource conflict", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, code="CONFLICT", status_code=409, details=details)


class UnauthorizedError(AppError):
    def __init__(
        self,
        message: str = "Authentication required",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="UNAUTHORIZED", status_code=401, details=details)


class ForbiddenError(AppError):
    def __init__(
        self, message: str = "Permission denied", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, code="FORBIDDEN", status_code=403, details=details)


class ValidationFailedError(AppError):
    def __init__(
        self, message: str = "Validation failed", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message, code="VALIDATION_FAILED", status_code=422, details=details
        )


class RateLimitedError(AppError):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code="RATE_LIMITED", status_code=429, details=details)


class UpstreamProviderError(AppError):
    def __init__(
        self,
        message: str = "Upstream provider error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message, code="UPSTREAM_PROVIDER_ERROR", status_code=502, details=details
        )
