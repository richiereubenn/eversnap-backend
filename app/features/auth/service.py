from flask import current_app
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
            current_app.logger.warning(f"Registration failed: Email '{data['email']}' already exists")
            raise EmailAlreadyExistsError()
        if UserRepository.find_by_username(data["username"]):
            current_app.logger.warning(f"Registration failed: Username '{data['username']}' already taken")
            raise UsernameAlreadyTakenError()

        user = User(username=data["username"], email=data["email"])
        user.set_password(data["password"])
        saved_user = UserRepository.save(user)
        current_app.logger.info(f"Admin registered successfully: ID {saved_user.id}, Username: '{saved_user.username}', Email: '{saved_user.email}'")
        return saved_user

    @staticmethod
    def authenticate(email: str, password: str) -> User:
        """
        Validasi kredensial login.
        Raises InvalidCredentialsError jika email/password salah.
        """
        user = UserRepository.find_by_email(email)
        if not user or not user.check_password(password):
            current_app.logger.warning(f"Failed login attempt for email: '{email}'")
            raise InvalidCredentialsError()
        current_app.logger.info(f"User login successful for email: '{email}', User ID: {user.id}")
        return user

    @staticmethod
    def get_or_404(user_id: int) -> User:
        """Ambil user berdasarkan ID. Raises UserNotFoundError jika tidak ada."""
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

