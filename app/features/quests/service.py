from app.features.quests.model import Quest
from app.features.quests.repository import QuestRepository
from app.features.quests.exceptions import QuestNotFoundError


class QuestService:
    """Business logic untuk manajemen quest dalam event."""

    @staticmethod
    def list_for_event(event_id: int, filters: dict) -> list:
        """List quest dengan filter opsional."""
        return QuestRepository.list_filtered(event_id, filters)

    @staticmethod
    def get_or_404(quest_id: int, event_id: int) -> Quest:
        """Ambil quest. Raises QuestNotFoundError jika tidak ada."""
        quest = QuestRepository.find(quest_id, event_id)
        if not quest:
            raise QuestNotFoundError()
        return quest

    @staticmethod
    def create(quest: Quest, event_id: int) -> Quest:
        """Simpan quest baru."""
        quest.event_id = event_id
        return QuestRepository.save(quest)

    @staticmethod
    def update(quest: Quest, event_id: int) -> Quest:
        """Commit perubahan quest."""
        QuestRepository.commit()
        return quest

    @staticmethod
    def delete(quest: Quest) -> None:
        """Hapus quest dari database."""
        QuestRepository.delete(quest)

    @staticmethod
    def toggle_field(quest: Quest, field: str) -> Quest:
        """Toggle nilai boolean field (is_active)."""
        setattr(quest, field, not getattr(quest, field))
        QuestRepository.commit()
        return quest

    @staticmethod
    def reorder(event_id: int, items: list) -> list:
        """Reorder quest berdasarkan list [{id, order_number}]."""
        for item in items:
            quest = QuestRepository.find(item.get("id"), event_id)
            if quest:
                quest.order_number = int(item.get("order_number", 0))
        QuestRepository.commit()
        return QuestRepository.list_ordered(event_id)
