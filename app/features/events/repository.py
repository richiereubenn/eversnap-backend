from app.extensions import db
from app.features.events.model import Event


class EventRepository:
    """Data access layer for Event model."""

    @staticmethod
    def list_by_user(user_id: int) -> list:
        return Event.query.filter_by(user_id=user_id).order_by(Event.created_at.desc()).all()

    @staticmethod
    def find(event_id: int, user_id: int) -> Event | None:
        return Event.query.filter_by(id=event_id, user_id=user_id).first()

    @staticmethod
    def find_by_id(event_id: int) -> Event | None:
        """Find event by ID without user ownership check (for guest access)."""
        return db.session.get(Event, event_id)

    @staticmethod
    def save(event: Event) -> Event:
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def commit() -> None:
        db.session.commit()

    @staticmethod
    def delete(event: Event) -> None:
        db.session.delete(event)
        db.session.commit()
