# f1_api/utils/exceptions.py

class APIError(Exception):
    """Custom exception for API errors with HTTP status codes."""

    status_code = 400

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message

    def to_dict(self) -> dict:
        return {"error": self.message}
