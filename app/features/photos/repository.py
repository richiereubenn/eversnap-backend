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

    @staticmethod
    def list_done_by_event(event_id: int) -> list:
        """Ambil semua foto berstatus 'done' milik sebuah event, urut terbaru.
        Digunakan sebagai initial snapshot saat client SSE pertama kali connect.
        """
        from app.features.guest_quests.model import GuestQuest
        from app.features.guests.model import Guest

        return (
            db.session.query(Photo)
            .join(GuestQuest, Photo.guest_quest_id == GuestQuest.id)
            .join(Guest, GuestQuest.guest_id == Guest.id)
            .filter(
                Guest.event_id == event_id,
                Photo.status == "done",
            )
            .order_by(Photo.created_at.desc())
            .all()
        )
