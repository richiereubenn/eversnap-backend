import os
import json
import qrcode
from flask import current_app

from datetime import datetime, timezone

from app.features.events.model import Event
from app.features.events.repository import EventRepository
from app.features.events.exceptions import EventNotFoundError, EventStartedError
from app.shared.cache import cache_get, cache_set, cache_delete


def _event_cache_key(event_id: int) -> str:
    """Menghasilkan Redis key untuk cache data event publik."""
    return f"event:public:{event_id}"


class EventService:
    """Business logic untuk manajemen event."""

    @staticmethod
    def list_for_user(user_id: int) -> list:
        """Ambil semua event milik user, urut terbaru."""
        return EventRepository.list_by_user(user_id)

    @staticmethod
    def get_or_404(event_id: int, user_id: int) -> Event:
        """Ambil event milik user. Raises EventNotFoundError jika tidak ada."""
        event = EventRepository.find(event_id, user_id)
        if not event:
            raise EventNotFoundError()
        return event

    @staticmethod
    def create(event: Event, user_id: int) -> Event:
        """Simpan event baru (instance sudah di-load dari schema)."""
        event.user_id = user_id
        saved_event = EventRepository.save(event)
        current_app.logger.info(f"Event created successfully: ID {saved_event.id}, Name: '{saved_event.name}', User ID: {user_id}")
        return saved_event

    @staticmethod
    def save(event: Event) -> Event:
        """Commit perubahan event yang sudah dimodifikasi & invalidate cache."""
        EventRepository.commit()
        # Hapus cache lama agar tamu mendapatkan data terbaru setelah event diubah
        cache_delete(_event_cache_key(event.id))
        current_app.logger.info(f"Event updated and cache invalidated: ID {event.id}, Name: '{event.name}'")
        return event

    @staticmethod
    def delete(event: Event) -> None:
        """Hapus event beserta semua quest-nya (cascade) & invalidate cache."""
        event_id = event.id
        event_name = event.name
        EventRepository.delete(event)
        cache_delete(_event_cache_key(event_id))
        current_app.logger.info(f"Event deleted successfully and cache invalidated: ID {event_id}, Name: '{event_name}'")

    @staticmethod
    def find_public(event_id: int) -> Event:
        """
        Ambil event berdasarkan ID tanpa cek kepemilikan (untuk akses tamu).
        Menggunakan Redis cache agar DB tidak dibebani saat banyak tamu scan QR sekaligus.
        Cache-Aside Pattern: cek cache dulu, jika miss baru query ke DB lalu simpan ke cache.
        """
        cache_key = _event_cache_key(event_id)

        # 1. Cek Redis cache dulu
        cached = cache_get(cache_key)
        if cached is not None:
            current_app.logger.info(f"[Cache] HIT for event {event_id}")
            # Bangun ulang Event object dari data cache
            event = EventRepository.find_by_id(event_id)
            if event:
                return event

        # 2. Cache miss — query ke database
        current_app.logger.info(f"[Cache] MISS for event {event_id}, querying DB")
        event = EventRepository.find_by_id(event_id)
        if not event:
            raise EventNotFoundError()

        # 3. Simpan data ringkas ke Redis dengan TTL dari config
        ttl = current_app.config.get("REDIS_EVENT_CACHE_TTL", 3600)
        cache_set(cache_key, {"id": event.id, "name": event.name}, ttl=ttl)

        return event


    @staticmethod
    def ensure_not_started(event: Event) -> None:
        """Raise EventStartedError jika event sudah melewati start_date."""
        if event.start_date and datetime.now(timezone.utc) >= event.start_date:
            raise EventStartedError()

    @staticmethod
    def get_or_generate_qr_url(event: Event) -> str:
        """Generate QR jika belum ada, lalu return URL publik-nya."""
        if not event.qr_code_path:
            event.qr_code_path = EventService._generate_qr(event.id)
            EventRepository.commit()
        return f"{current_app.config['BASE_URL']}/uploads/{event.qr_code_path}"

    @staticmethod
    def _generate_qr(event_id: int) -> str:
        """Generate QR code PNG untuk event. Return path relatif dari uploads/."""
        qr_dir = current_app.config["QR_FOLDER"]
        os.makedirs(qr_dir, exist_ok=True)

        event_url = f"{current_app.config['BASE_URL']}/guest/event/{event_id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(event_url)
        qr.make(fit=True)

        img      = qr.make_image(fill_color="black", back_color="white")
        filename = f"event_{event_id}.png"
        img.save(os.path.join(qr_dir, filename))
        current_app.logger.info(f"QR Code generated for event ID: {event_id}")
        return f"qr/{filename}"

    @staticmethod
    def get_dashboard_stats(event: Event) -> dict:
        """Hitung statistik ringkas event dari quests yang ada."""
        quests = event.quests
        total  = len(quests)
        active = sum(1 for q in quests if q.is_active)
        return {
            "total_quests":    total,
            "active_quests":   active,
            "inactive_quests": total - active,
        }
