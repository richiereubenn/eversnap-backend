from app.extensions import db
from app.features.quests.model import Quest


class QuestRepository:
    """Data access layer for Quest model."""

    @staticmethod
    def list_by_event(event_id: int) -> list:
        """Unfiltered list, ordered by order_number then created_at."""
        return (
            Quest.query.filter_by(event_id=event_id)
            .order_by(Quest.order_number.asc(), Quest.created_at.asc())
            .all()
        )

    @staticmethod
    def list_filtered(event_id: int, filters: dict) -> list:
        """List with optional filters: active."""
        query = Quest.query.filter_by(event_id=event_id)

        if filters.get("active") is not None:
            query = query.filter_by(is_active=filters["active"])

        return query.order_by(Quest.order_number.asc(), Quest.created_at.asc()).all()

    @staticmethod
    def find(quest_id: int, event_id: int) -> Quest | None:
        return Quest.query.filter_by(id=quest_id, event_id=event_id).first()

    @staticmethod
    def find_by_id_in_event(quest_id: int, event_id: int) -> Quest | None:
        """Alias for find — explicit name."""
        return Quest.query.filter_by(id=quest_id, event_id=event_id).first()

    @staticmethod
    def save(quest: Quest) -> Quest:
        db.session.add(quest)
        db.session.commit()
        return quest

    @staticmethod
    def commit() -> None:
        db.session.commit()

    @staticmethod
    def delete(quest: Quest) -> None:
        db.session.delete(quest)
        db.session.commit()

    @staticmethod
    def list_ordered(event_id: int) -> list:
        """List all quests ordered by order_number (used after reorder)."""
        return Quest.query.filter_by(event_id=event_id).order_by(Quest.order_number).all()
