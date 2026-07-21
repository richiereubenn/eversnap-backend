"""
Redis Pub/Sub helper untuk fitur Live Photo Wall.

Modul ini menjembatani komunikasi antar-proses antara:
- RQ Worker (Publisher): Mengirim notifikasi setelah foto selesai diproses.
- Flask SSE Endpoint (Subscriber): Mendengarkan notifikasi dan meneruskannya ke browser.

Menggunakan Redis Pub/Sub karena:
1. RQ Worker dan Flask Web Server berjalan di proses/kontainer TERPISAH.
2. Komunikasi langsung antar proses tidak dimungkinkan.
3. Redis sudah tersedia di infrastruktur sebagai broker RQ.
"""
import json
import redis as redis_lib


def _get_raw_redis(redis_url: str) -> redis_lib.Redis:
    """Buat koneksi Redis raw (bukan decode_responses) untuk Pub/Sub."""
    return redis_lib.from_url(redis_url, decode_responses=False)


def publish_photo_event(redis_url: str, channel_prefix: str, event_id: int, photo_data: dict) -> None:
    """
    Publish notifikasi foto baru ke Redis Pub/Sub channel.
    Dipanggil oleh RQ Worker setelah photo berhasil diproses.

    Args:
        redis_url     : URL koneksi Redis (dari config).
        channel_prefix: Prefix channel, misal "live:event:".
        event_id      : ID event pemilik foto.
        photo_data    : Dict berisi data foto yang akan dikirim ke client SSE.
    """
    try:
        r = _get_raw_redis(redis_url)
        channel = f"{channel_prefix}{event_id}"
        message = json.dumps(photo_data, default=str)
        r.publish(channel, message)
    except Exception as e:
        # Pub/Sub failure tidak boleh gagalkan job utama — hanya log warning
        import logging
        logging.getLogger(__name__).warning(
            f"[PubSub] Gagal publish ke channel live:event:{event_id}: {e}"
        )


def make_redis_pubsub(redis_url: str, channel_prefix: str, event_id: int):
    """
    Buat objek PubSub Redis dan subscribe ke channel event tertentu.
    Dipanggil oleh SSE endpoint (Flask) untuk mulai mendengarkan.

    Args:
        redis_url     : URL koneksi Redis (dari config).
        channel_prefix: Prefix channel, misal "live:event:".
        event_id      : ID event yang ingin di-subscribe.

    Returns:
        Tuple (redis.Redis instance, redis.client.PubSub instance)
    """
    r = _get_raw_redis(redis_url)
    pubsub = r.pubsub()
    channel = f"{channel_prefix}{event_id}"
    pubsub.subscribe(channel)
    return r, pubsub
