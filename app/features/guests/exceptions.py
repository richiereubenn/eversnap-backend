class GuestNotFoundError(Exception):
    """Raised when a guest cannot be found."""

    def __init__(self, message: str = "Guest not found"):
        super().__init__(message)


class GuestQuestNotFoundError(Exception):
    """Raised when a guest-quest record cannot be found."""

    def __init__(self, message: str = "Guest quest record not found"):
        super().__init__(message)
