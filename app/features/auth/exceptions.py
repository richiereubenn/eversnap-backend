class EmailAlreadyExistsError(Exception):
    """Raised when attempting to register with an email that's already in use."""

    def __init__(self, message: str = "Email already registered"):
        super().__init__(message)


class UsernameAlreadyTakenError(Exception):
    """Raised when attempting to register with a username that's already taken."""

    def __init__(self, message: str = "Username already taken"):
        super().__init__(message)


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)


class UserNotFoundError(Exception):
    """Raised when a user cannot be found by the given identifier."""

    def __init__(self, message: str = "User not found"):
        super().__init__(message)
