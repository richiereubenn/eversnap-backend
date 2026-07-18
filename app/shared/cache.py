import json
import redis
from flask import current_app


def get_redis() -> redis.Redis:
    """Ambil instance Redis dari config Flask app."""
    return redis.from_url(
        current_app.config["REDIS_URL"],
        decode_responses=True,
    )


def cache_get(key: str):
    """
    Ambil data dari Redis cache.
    Return dict/list jika ditemukan, None jika tidak ada atau Redis error.
    """
    try:
        r = get_redis()
        data = r.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        current_app.logger.warning(f"[Cache] GET failed for key '{key}': {e}")
        return None


def cache_set(key: str, value, ttl: int = 3600) -> None:
    """
    Simpan data ke Redis cache.
    ttl: Waktu kedaluwarsa dalam detik (default 1 jam).
    Jika Redis error, diabaikan dan tidak akan mengganggu flow utama.
    """
    try:
        r = get_redis()
        r.setex(key, ttl, json.dumps(value, default=str))
    except Exception as e:
        current_app.logger.warning(f"[Cache] SET failed for key '{key}': {e}")


def cache_delete(key: str) -> None:
    """
    Hapus satu key dari Redis cache (Cache Invalidation).
    Jika Redis error, diabaikan.
    """
    try:
        r = get_redis()
        r.delete(key)
        current_app.logger.info(f"[Cache] Invalidated key '{key}'")
    except Exception as e:
        current_app.logger.warning(f"[Cache] DELETE failed for key '{key}': {e}")
