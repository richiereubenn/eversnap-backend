from app.extensions import db
from app.features.photos.model import Photo


class PhotoRepository:
    """Data access layer for Photo model."""

    @staticmethod
    def save(photo: Photo) -> Photo:
        db.session.add(photo)
        db.session.commit()
        return photo

    @staticmethod
    def list_by_guest_quest(guest_quest_id: int) -> list:
        return Photo.query.filter_by(guest_quest_id=guest_quest_id).all()
