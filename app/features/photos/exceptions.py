class PhotoNotFoundError(Exception):
    """Raised when a photo cannot be found."""

    def __init__(self, message: str = "Photo not found"):
        super().__init__(message)


class PhotoStreamError(Exception):
    """Raised when the SSE live stream encounters a fatal error."""

    def __init__(self, message: str = "Live photo stream error"):
        super().__init__(message)
