"""Instagram API and publishing custom exceptions."""


class InstagramException(Exception):
    """Base exception for Instagram operations."""
    pass


class InstagramPublishingDisabledError(InstagramException):
    """Raised when publishing is attempted but INSTAGRAM_PUBLISH_ENABLED=false."""
    pass


class InstagramAPIError(InstagramException):
    """Raised when Meta Graph API returns an error response."""

    def __init__(self, message: str, status_code: int = 400, error_subcode: int = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_subcode = error_subcode


class InstagramTokenExpiredError(InstagramAPIError):
    """Raised when the User Access Token is invalid or expired (code 190)."""
    pass


class InstagramMediaUploadError(InstagramAPIError):
    """Raised when image container creation fails."""
    pass
