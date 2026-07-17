from app.extensions import db
from app.features.guest_quests.model import GuestQuest


class GuestQuestRepository:
    """Data access layer for GuestQuest model."""

    @staticmethod
    def find(guest_id: int, quest_id: int) -> GuestQuest | None:
        return GuestQuest.query.filter_by(guest_id=guest_id, quest_id=quest_id).first()

    @staticmethod
    def find_by_id(gq_id: int) -> GuestQuest | None:
        return db.session.get(GuestQuest, gq_id)

    @staticmethod
    def list_by_guest(guest_id: int) -> list:
        return GuestQuest.query.filter_by(guest_id=guest_id).all()

    @staticmethod
    def save(guest_quest: GuestQuest) -> GuestQuest:
        db.session.add(guest_quest)
        db.session.commit()
        return guest_quest

    @staticmethod
    def commit() -> None:
        db.session.commit()
