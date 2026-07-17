class QuestNotFoundError(Exception):
    """Raised when a quest cannot be found within the given event."""

    def __init__(self, message: str = "Quest not found"):
        super().__init__(message)
