# f1_api/utils/exceptions.py

from __future__ import annotations

from typing import Any


DEFAULT_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    500: "internal_error",
    502: "bad_gateway",
}


class APIError(Exception):
    """Custom exception for API errors with HTTP status codes."""

    status_code = 400

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message
        self.code = code
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        error_body: dict[str, Any] = {
            "status": self.status_code,
            "code": self.code or DEFAULT_ERROR_CODES.get(self.status_code, "error"),
            "message": self.message,
        }
        if self.details:
            error_body["details"] = self.details
        return {"error": error_body}
