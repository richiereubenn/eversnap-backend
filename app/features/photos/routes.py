from flask import Blueprint, Response, stream_with_context

from app.features.photos.service import PhotoService

photos_bp = Blueprint("photos", __name__)


@photos_bp.route("/<int:event_id>/live", methods=["GET"])
def live_photo_feed(event_id: int):
    """GET /api/events/<event_id>/live — SSE endpoint untuk Live Photo Wall.

    Endpoint publik (tanpa JWT) — dirancang untuk dibuka di layar proyektor/TV
    yang menampilkan foto tamu secara real-time.

    Response: text/event-stream

    Events yang dikirim:
    - event: connected      → konfirmasi koneksi berhasil
    - event: initial_photos → snapshot foto-foto yang sudah ada
    - event: new_photo      → foto baru selesai diproses oleh RQ Worker
    - event: heartbeat      → ping berkala untuk menjaga koneksi hidup
    - event: error          → error fatal pada stream
    """
    # Validasi event ada (PhotoNotFoundError → 404 via error_handlers)
    PhotoService.get_event_or_404(event_id)

    return Response(
        stream_with_context(PhotoService.stream_live_photos(event_id)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",   # Nonaktifkan buffering di Nginx
            "Connection":                  "keep-alive",
            "Access-Control-Allow-Origin": "*",    # Izinkan akses dari proyektor/TV
        },
    )
