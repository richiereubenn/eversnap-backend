from app.extensions import db
from app.features.auth.model import User


class UserRepository:
    """Data access layer for User model."""

    @staticmethod
    def find_by_email(email: str) -> User | None:
        return User.query.filter_by(email=email).first()

    @staticmethod
    def find_by_username(username: str) -> User | None:
        return User.query.filter_by(username=username).first()

    @staticmethod
    def find_by_id(user_id: int) -> User | None:
        return db.session.get(User, user_id)

    @staticmethod
    def save(user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user
