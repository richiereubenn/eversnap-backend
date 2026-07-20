from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import limiter
from app.features.events.schema import event_schema, events_schema
from app.features.events.service import EventService
from app.shared.responses import api_response

events_bp = Blueprint("events", __name__)


@events_bp.route("", methods=["GET"])
@jwt_required()
def list_events():
    """GET /api/events — List semua event milik user yang login."""
    user_id = int(get_jwt_identity())
    events  = EventService.list_for_user(user_id)
    return api_response(200, "Events retrieved successfully", events_schema.dump(events))


@events_bp.route("", methods=["POST"])
@jwt_required()
@limiter.limit("20 per minute")  # Sedang: admin tidak butuh buat banyak event dalam waktu singkat
def create_event():
    """POST /api/events — Buat event baru."""
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}

    # ValidationError → global handler → 422
    event = event_schema.load(data)

    event = EventService.create(event, user_id)
    return api_response(201, "Event created", event_schema.dump(event))


@events_bp.route("/<int:event_id>", methods=["GET"])
@jwt_required()
def get_event(event_id):
    """GET /api/events/<id> — Detail event."""
    user_id = int(get_jwt_identity())
    event   = EventService.get_or_404(event_id, user_id)  # EventNotFoundError → 404
    return api_response(200, "Event retrieved successfully", event_schema.dump(event))


@events_bp.route("/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_event(event_id):
    """PUT /api/events/<id> — Edit event."""
    user_id = int(get_jwt_identity())
    event   = EventService.get_or_404(event_id, user_id)

    data  = request.get_json(silent=True) or {}
    event = event_schema.load(data, instance=event, partial=True)  # ValidationError → 422

    EventService.save(event)
    return api_response(200, "Event updated", event_schema.dump(event))


@events_bp.route("/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_event(event_id):
    """DELETE /api/events/<id> — Hapus event beserta semua quest-nya."""
    user_id = int(get_jwt_identity())
    event   = EventService.get_or_404(event_id, user_id)
    EventService.delete(event)
    return api_response(200, "Event deleted")


@events_bp.route("/<int:event_id>/qr", methods=["GET"])
@jwt_required()
@limiter.limit("10 per minute")  # Ketat: operasi I/O berat (generate & simpan file PNG)
def get_qr(event_id):
    """GET /api/events/<id>/qr — Generate / ambil QR code event."""
    user_id = int(get_jwt_identity())
    event   = EventService.get_or_404(event_id, user_id)
    qr_url  = EventService.get_or_generate_qr_url(event)
    return api_response(200, "QR code retrieved successfully", {
        "event_id": event_id,
        "qr_url":   qr_url,
        "qr_path":  event.qr_code_path,
    })


@events_bp.route("/<int:event_id>/dashboard", methods=["GET"])
@jwt_required()
def dashboard(event_id):
    """GET /api/events/<id>/dashboard — Statistik ringkas event."""
    user_id = int(get_jwt_identity())
    event   = EventService.get_or_404(event_id, user_id)
    return api_response(200, "Dashboard stats retrieved successfully", {
        "event": event_schema.dump(event),
        "stats": EventService.get_dashboard_stats(event),
    })
