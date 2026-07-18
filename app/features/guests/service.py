import os
from flask import current_app

from app.features.guests.model import Guest
from app.features.guest_quests.model import GuestQuest
from app.features.photos.model import Photo
from app.features.guests.repository import GuestRepository
from app.features.guest_quests.repository import GuestQuestRepository
from app.features.photos.repository import PhotoRepository
from app.features.guests.exceptions import (
    GuestNotFoundError,
    GuestQuestNotFoundError,
)
from app.features.events.service import EventService
from app.extensions import db
from app.shared.upload import save_upload


class GuestService:
    """Business logic untuk manajemen guest dalam event."""

    # ── Guest ──────────────────────────────────────────────────────────────────

    @staticmethod
    def register_guest(event_id: int, name: str) -> Guest:
        """Daftarkan tamu baru ke event setelah scan QR."""
        # Pastikan event ada
        EventService.find_public(event_id)

        guest = Guest(event_id=event_id, name=name)
        saved_guest = GuestRepository.save(guest)
        current_app.logger.info(f"Guest registered successfully: ID {saved_guest.id}, Name: '{name}', Event ID: {event_id}")
        return saved_guest

    @staticmethod
    def get_or_404(guest_id: int) -> Guest:
        """Ambil guest. Raises GuestNotFoundError jika tidak ada."""
        guest = GuestRepository.find_by_id(guest_id)
        if not guest:
            raise GuestNotFoundError()
        return guest

    # ── GuestQuest ─────────────────────────────────────────────────────────────

    @staticmethod
    def list_quest_progress(guest: Guest) -> list:
        """
        List semua quest event beserta progress tamu.
        Return list dict berisi quest info + completion status.
        """
        event = EventService.find_public(guest.event_id)
        active_quests = [q for q in event.quests if q.is_active]

        # Map existing guest_quest records
        gq_map = {gq.quest_id: gq for gq in guest.guest_quests}

        result = []
        for quest in sorted(active_quests, key=lambda q: q.order_number):
            gq = gq_map.get(quest.id)
            result.append({
                "quest_id":    quest.id,
                "title":       quest.title,
                "order":       quest.order_number,
                "is_complete": gq.is_complete if gq else False,
                "message":     gq.message if gq else None,
                "guest_quest_id": gq.id if gq else None,
                "photos":      [
                    {
                        "id": p.id,
                        "photo_url": f"{current_app.config['BASE_URL']}/uploads/{p.url}",
                    }
                    for p in (gq.photos if gq else [])
                ],
            })
        return result


    # ── Photo ──────────────────────────────────────────────────────────────────

    @staticmethod
    def upload_photo(guest_id: int, quest_id: int, file) -> Photo:
        """Upload foto untuk quest tertentu milik tamu (1 quest 1 foto, otomatis complete)."""
        # Pastikan ada record guest_quest (buat jika belum)
        gq = GuestQuestRepository.find(guest_id, quest_id)
        if not gq:
            gq = GuestQuest(guest_id=guest_id, quest_id=quest_id, is_complete=True)
            GuestQuestRepository.save(gq)
        else:
            # Otomatis tandai sebagai lengkap
            gq.is_complete = True
            
            # Cari dan hapus foto lama (aturan 1 quest 1 foto)
            old_photos = PhotoRepository.list_by_guest_quest(gq.id)
            for old_photo in old_photos:
                # Hapus file fisik dari server
                file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], old_photo.url)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        current_app.logger.error(f"Failed to delete old photo file {file_path}: {e}")
                
                db.session.delete(old_photo)
            db.session.commit()

        # Simpan file via shared upload util
        relative_path = save_upload(file, "photos", prefix=f"g{guest_id}_q{quest_id}")
        if not relative_path:
            current_app.logger.warning(f"Failed photo upload: Invalid file format from Guest ID: {guest_id}, Quest ID: {quest_id}")
            raise ValueError("Invalid file. Allowed: png, jpg, jpeg, gif, webp")

        photo = Photo(
            guest_quest_id=gq.id,
            url=relative_path,
            file_size=file.content_length or None,
        )
        saved_photo = PhotoRepository.save(photo)
        current_app.logger.info(f"Photo uploaded successfully: ID {saved_photo.id}, Guest ID: {guest_id}, Quest ID: {quest_id}, Path: '{relative_path}'")
        return saved_photo
