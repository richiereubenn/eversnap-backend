from app.features.auth.model import User
from app.features.auth.repository import UserRepository
from app.features.auth.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyTakenError,
    InvalidCredentialsError,
    UserNotFoundError,
)


class AuthService:
    """Business logic untuk autentikasi dan manajemen akun admin."""

    @staticmethod
    def register(data: dict) -> User:
        """
        Buat akun admin baru.
        Raises EmailAlreadyExistsError / UsernameAlreadyTakenError jika duplikat.
        """
        if UserRepository.find_by_email(data["email"]):
            raise EmailAlreadyExistsError()
        if UserRepository.find_by_username(data["username"]):
            raise UsernameAlreadyTakenError()

        user = User(username=data["username"], email=data["email"])
        user.set_password(data["password"])
        return UserRepository.save(user)

    @staticmethod
    def authenticate(email: str, password: str) -> User:
        """
        Validasi kredensial login.
        Raises InvalidCredentialsError jika email/password salah.
        """
        user = UserRepository.find_by_email(email)
        if not user or not user.check_password(password):
            raise InvalidCredentialsError()
        return user

    @staticmethod
    def get_or_404(user_id: int) -> User:
        """Ambil user berdasarkan ID. Raises UserNotFoundError jika tidak ada."""
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user
