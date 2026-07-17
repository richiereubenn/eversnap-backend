class EventNotFoundError(Exception):
    """Raised when an event cannot be found or doesn't belong to the user."""

    def __init__(self, message: str = "Event not found"):
        super().__init__(message)


class EventStartedError(Exception):
    """Raised when trying to modify quests after event start_date has passed."""

    def __init__(self, message: str = "Event has already started. Quest modifications are locked."):
        super().__init__(message)
