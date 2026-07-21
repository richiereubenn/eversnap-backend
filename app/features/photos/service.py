"""
Business logic untuk fitur Live Photo Wall.

Semua logic SSE (stream generator, formatting, Pub/Sub subscribe) diletakkan
di sini agar routes.py tetap tipis — konsisten dengan pola service layer
yang digunakan oleh fitur lain (events, guests, quests).
"""
import json
import time
import logging

from flask import current_app

from app.features.photos.repository import PhotoRepository
from app.features.events.repository import EventRepository
from app.features.photos.exceptions import PhotoNotFoundError

logger = logging.getLogger(__name__)


class PhotoService:
    """Business logic untuk Photo dan Live Photo Wall (SSE)."""

    # ── Live Feed ──────────────────────────────────────────────────────────────

    @staticmethod
    def get_event_or_404(event_id: int):
        """Ambil event berdasarkan ID. Raises PhotoNotFoundError jika tidak ditemukan."""
        event = EventRepository.find_by_id(event_id)
        if not event:
            raise PhotoNotFoundError(f"Event with ID {event_id} not found")
        return event

    @staticmethod
    def get_initial_photos(event_id: int) -> list[dict]:
        """
        Ambil snapshot foto-foto yang sudah selesai diproses untuk sebuah event.
        Dipanggil sekali saat client SSE pertama kali connect.
        """
        base_url = current_app.config["BASE_URL"]
        photos   = PhotoRepository.list_done_by_event(event_id)

        result = []
        for p in photos:
            result.append({
                "photo_id":      p.id,
                "photo_url":     f"{base_url}/uploads/{p.url}",
                "thumbnail_url": (
                    f"{base_url}/uploads/{p.thumbnail_url}" if p.thumbnail_url else None
                ),
                "status":        p.status,
                "created_at":    str(p.created_at),
                "guest_name":    p.guest_quest.guest.name,
            })
        return result

    @staticmethod
    def build_sse_message(data: dict | str, event: str | None = None) -> str:
        """
        Format pesan sesuai spesifikasi SSE (text/event-stream).

        Contoh output:
            event: new_photo
            data: {"photo_id": 1, ...}

        """
        lines = []
        if event:
            lines.append(f"event: {event}")
        if isinstance(data, dict):
            lines.append(f"data: {json.dumps(data, default=str)}")
        else:
            lines.append(f"data: {data}")
        lines.append("")  # Blank line = penanda akhir SSE message
        return "\n".join(lines) + "\n"

    @staticmethod
    def stream_live_photos(event_id: int):
        """
        Generator SSE untuk Live Photo Wall.

        Alur:
        1. Kirim konfirmasi koneksi (event: connected)
        2. Kirim snapshot foto yang sudah ada (event: initial_photos)
        3. Subscribe ke Redis Pub/Sub channel live:event:<event_id>
        4. Forward setiap pesan foto baru (event: new_photo) ke client
        5. Kirim heartbeat berkala agar koneksi tidak mati oleh proxy/firewall
        """
        redis_url      = current_app.config["REDIS_URL"]
        channel_prefix = current_app.config["LIVE_CHANNEL_PREFIX"]
        heartbeat_secs = current_app.config["SSE_HEARTBEAT_INTERVAL"]

        # ── 1. Konfirmasi koneksi ───────────────────────────────────────────
        yield PhotoService.build_sse_message(
            {"message": "Connected to live photo feed", "event_id": event_id},
            event="connected",
        )

        # ── 2. Initial snapshot foto yang sudah ada ─────────────────────────
        try:
            existing = PhotoService.get_initial_photos(event_id)
            yield PhotoService.build_sse_message(
                {"photos": existing, "total": len(existing)},
                event="initial_photos",
            )
        except Exception as e:
            logger.warning(f"[SSE] Gagal ambil initial photos untuk event {event_id}: {e}")
            yield PhotoService.build_sse_message(
                {"photos": [], "total": 0},
                event="initial_photos",
            )

        # ── 3. Subscribe ke Redis Pub/Sub dan stream foto baru ──────────────
        from app.shared.pubsub import make_redis_pubsub

        r      = None
        pubsub = None
        try:
            r, pubsub      = make_redis_pubsub(redis_url, channel_prefix, event_id)
            last_heartbeat = time.time()

            while True:
                # get_message dengan timeout 1 detik agar heartbeat tetap bisa dikirim
                message = pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )

                if message and message["type"] == "message":
                    try:
                        raw = message["data"]
                        if isinstance(raw, bytes):
                            raw = raw.decode("utf-8")
                        photo_data = json.loads(raw)
                        yield PhotoService.build_sse_message(photo_data, event="new_photo")
                    except Exception as parse_err:
                        logger.warning(f"[SSE] Gagal parse pesan Pub/Sub: {parse_err}")

                # Kirim heartbeat setiap SSE_HEARTBEAT_INTERVAL detik
                now = time.time()
                if now - last_heartbeat >= heartbeat_secs:
                    yield PhotoService.build_sse_message("ping", event="heartbeat")
                    last_heartbeat = now

        except GeneratorExit:
            logger.info(f"[SSE] Client disconnected dari event {event_id}")
        except Exception as e:
            logger.error(f"[SSE] Error pada stream event {event_id}: {e}")
            yield PhotoService.build_sse_message(
                {"error": "Stream interrupted"},
                event="error",
            )
        finally:
            if pubsub:
                try:
                    pubsub.unsubscribe()
                    pubsub.close()
                except Exception:
                    pass
            if r:
                try:
                    r.close()
                except Exception:
                    pass
