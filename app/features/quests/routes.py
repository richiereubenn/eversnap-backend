from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import limiter
from app.features.events.service import EventService
from app.features.quests.schema import quest_schema, quests_schema
from app.features.quests.service import QuestService
from app.shared.responses import api_response

quests_bp = Blueprint("quests", __name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_form_data(form: dict) -> dict:
    """Convert multipart form-data strings ke tipe Python yang tepat."""
    data = dict(form)
    for field in ("is_active",):
        if field in data:
            data[field] = data[field].lower() in ("true", "1", "yes")
    for field in ("order_number",):
        if field in data:
            try:
                data[field] = int(data[field])
            except ValueError:
                pass
    return data


def _parse_request_data() -> dict:
    """Parse JSON atau multipart form-data secara otomatis."""
    if request.content_type and "multipart" in request.content_type:
        return _parse_form_data(request.form.to_dict())
    return request.get_json(silent=True) or {}


def _parse_bool_filter(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() == "true"


# ── Routes ─────────────────────────────────────────────────────────────────────

@quests_bp.route("/<int:event_id>/quests", methods=["GET"])
@jwt_required()
def list_quests(event_id):
    """GET /api/events/<event_id>/quests — List quest dalam event."""
    user_id = int(get_jwt_identity())
    EventService.get_or_404(event_id, user_id)  # EventNotFoundError → 404

    filters = {
        "active":          _parse_bool_filter(request.args.get("active")),
    }

    quests = QuestService.list_for_event(event_id, filters)
    return api_response(200, "Quests retrieved successfully", quests_schema.dump(quests))


@quests_bp.route("/<int:event_id>/quests", methods=["POST"])
@jwt_required()
@limiter.limit("30 per minute")  # Sedang: operasi write ke DB
def create_quest(event_id):
    """POST /api/events/<event_id>/quests — Buat quest baru."""
    user_id = int(get_jwt_identity())
    event = EventService.get_or_404(event_id, user_id)
    EventService.ensure_not_started(event)

    data  = _parse_request_data()
    quest = quest_schema.load(data)  # ValidationError → 422

    quest = QuestService.create(quest, event_id)
    return api_response(201, "Quest created", quest_schema.dump(quest))


@quests_bp.route("/<int:event_id>/quests/<int:quest_id>", methods=["GET"])
@jwt_required()
def get_quest(event_id, quest_id):
    """GET /api/events/<event_id>/quests/<quest_id> — Detail quest."""
    user_id = int(get_jwt_identity())
    EventService.get_or_404(event_id, user_id)
    quest = QuestService.get_or_404(quest_id, event_id)  # QuestNotFoundError → 404
    return api_response(200, "Quest retrieved successfully", quest_schema.dump(quest))


@quests_bp.route("/<int:event_id>/quests/<int:quest_id>", methods=["PUT"])
@jwt_required()
@limiter.limit("30 per minute")  # Sedang: operasi write ke DB
def update_quest(event_id, quest_id):
    """PUT /api/events/<event_id>/quests/<quest_id> — Edit quest."""
    user_id = int(get_jwt_identity())
    event = EventService.get_or_404(event_id, user_id)
    EventService.ensure_not_started(event)
    quest = QuestService.get_or_404(quest_id, event_id)

    data  = _parse_request_data()
    quest = quest_schema.load(data, instance=quest, partial=True)  # ValidationError → 422

    quest = QuestService.update(quest, event_id)
    return api_response(200, "Quest updated", quest_schema.dump(quest))


@quests_bp.route("/<int:event_id>/quests/<int:quest_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit("30 per minute")  # Sedang: operasi write ke DB
def delete_quest(event_id, quest_id):
    """DELETE /api/events/<event_id>/quests/<quest_id> — Hapus quest."""
    user_id = int(get_jwt_identity())
    event = EventService.get_or_404(event_id, user_id)
    EventService.ensure_not_started(event)
    quest = QuestService.get_or_404(quest_id, event_id)
    QuestService.delete(quest)
    return api_response(200, "Quest deleted")



@quests_bp.route("/<int:event_id>/quests/<int:quest_id>/toggle-active", methods=["PATCH"])
@jwt_required()
@limiter.limit("30 per minute")  # Sedang: operasi write ke DB
def toggle_active(event_id, quest_id):
    """PATCH — Toggle is_active pada quest."""
    user_id = int(get_jwt_identity())
    event = EventService.get_or_404(event_id, user_id)
    EventService.ensure_not_started(event)
    quest = QuestService.get_or_404(quest_id, event_id)
    quest = QuestService.toggle_field(quest, "is_active")
    return api_response(200, f"Quest active status toggled", {
        "quest_id":  quest.id,
        "is_active": quest.is_active,
    })


@quests_bp.route("/<int:event_id>/quests/reorder", methods=["PATCH"])
@jwt_required()
@limiter.limit("30 per minute")  # Sedang: operasi write ke DB
def reorder_quests(event_id):
    """PATCH — Reorder quests: body = [{id, order_number}, ...]."""
    user_id = int(get_jwt_identity())
    event = EventService.get_or_404(event_id, user_id)
    EventService.ensure_not_started(event)

    items = request.get_json(silent=True) or []
    if not isinstance(items, list):
        return api_response(400, "Expected a list of {id, order_number}")

    quests = QuestService.reorder(event_id, items)
    return api_response(200, "Quests reordered", quests_schema.dump(quests))
