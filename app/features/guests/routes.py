from flask import Blueprint, request, jsonify

from app.extensions import limiter
from app.features.events.service import EventService
from app.features.events.schema import event_schema
from app.features.guests.schema import guest_schema
from app.features.guests.service import GuestService
from app.features.quests.schema import quests_schema

guests_bp = Blueprint("guests", __name__)


# ── Join Event ─────────────────────────────────────────────────────────────────

@guests_bp.route("/event/<int:event_id>/join", methods=["POST"])
@limiter.limit("20 per minute")  # Sedang: cegah spam pendaftaran tamu palsu
def join_event(event_id):
    """POST /api/guest/event/<event_id>/join — Tamu scan QR, isi nama, join event."""
    data = request.get_json(silent=True) or {}

    # Validasi nama
    validated = guest_schema.load(data)  # ValidationError → 422

    guest = GuestService.register_guest(event_id, validated.name)
    return jsonify({
        "message":  "Welcome! You have joined the event.",
        "guest":    guest_schema.dump(guest),
        "event_id": event_id,
    }), 201


# ── View Event Detail ──────────────────────────────────────────────────────────

@guests_bp.route("/<int:guest_id>/event", methods=["GET"])
def view_event(guest_id):
    """GET /api/guest/<guest_id>/event — Lihat detail event + quest list."""
    guest = GuestService.get_or_404(guest_id)
    event = EventService.find_public(guest.event_id)
    return jsonify({
        "event":  event_schema.dump(event),
        "guest":  guest_schema.dump(guest),
    }), 200


# ── View Quest Progress ───────────────────────────────────────────────────────

@guests_bp.route("/<int:guest_id>/quests", methods=["GET"])
def view_quests(guest_id):
    """GET /api/guest/<guest_id>/quests — Lihat semua quest + progress completion."""
    guest    = GuestService.get_or_404(guest_id)
    progress = GuestService.list_quest_progress(guest)
    return jsonify({
        "guest":  guest_schema.dump(guest),
        "quests": progress,
    }), 200

# ── Upload Photo ───────────────────────────────────────────────────────────────

@guests_bp.route("/<int:guest_id>/quests/<int:quest_id>/photos", methods=["POST"])
@limiter.limit("10 per minute")
def upload_photo(guest_id, quest_id):
    """POST /api/guest/<guest_id>/quests/<quest_id>/photos — Upload foto untuk quest."""
    guest = GuestService.get_or_404(guest_id)

    if "photo" not in request.files:
        return jsonify({"error": "No photo file provided. Use key 'photo' in form-data."}), 400

    file  = request.files["photo"]
    photo = GuestService.upload_photo(guest.id, quest_id, file)

    from app.features.photos.schema import photo_schema
    return jsonify({
        "message": "Photo accepted and is being processed in the background.",
        "photo":   photo_schema.dump(photo),
    }), 202
