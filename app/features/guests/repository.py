from app.extensions import db
from app.features.guests.model import Guest


class GuestRepository:
    """Data access layer for Guest model."""

    @staticmethod
    def find_by_id(guest_id: int) -> Guest | None:
        return db.session.get(Guest, guest_id)

    @staticmethod
    def list_by_event(event_id: int) -> list:
        return Guest.query.filter_by(event_id=event_id).order_by(Guest.created_at.desc()).all()

    @staticmethod
    def save(guest: Guest) -> Guest:
        db.session.add(guest)
        db.session.commit()
        return guest

    @staticmethod
    def commit() -> None:
        db.session.commit()
