import logging
from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app.features.auth.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyTakenError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.features.events.exceptions import EventNotFoundError, EventStartedError
from app.features.quests.exceptions import QuestNotFoundError
from app.features.guests.exceptions import (
    GuestNotFoundError,
    GuestQuestNotFoundError,
)

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Daftarkan semua error handler ke Flask app — satu tempat untuk semua."""

    # ── 422 Validation ─────────────────────────────────────────
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({"errors": error.messages}), 422

    # ── 401 Unauthorized ───────────────────────────────────────
    @app.errorhandler(InvalidCredentialsError)
    def handle_invalid_credentials(error):
        return jsonify({"error": str(error)}), 401

    # ── 409 Conflict ───────────────────────────────────────────
    @app.errorhandler(EmailAlreadyExistsError)
    def handle_email_exists(error):
        return jsonify({"error": str(error)}), 409

    @app.errorhandler(UsernameAlreadyTakenError)
    def handle_username_taken(error):
        return jsonify({"error": str(error)}), 409

    # ── 404 Not Found ──────────────────────────────────────────
    @app.errorhandler(UserNotFoundError)
    def handle_user_not_found(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(EventNotFoundError)
    def handle_event_not_found(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(QuestNotFoundError)
    def handle_quest_not_found(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(GuestNotFoundError)
    def handle_guest_not_found(error):
        return jsonify({"error": str(error)}), 404

    @app.errorhandler(GuestQuestNotFoundError)
    def handle_guest_quest_not_found(error):
        return jsonify({"error": str(error)}), 404

    # ── 403 Forbidden ──────────────────────────────────────────
    @app.errorhandler(EventStartedError)
    def handle_event_started(error):
        return jsonify({"error": str(error)}), 403


    # ── Flask HTTP exceptions (404, 405, etc.) ─────────────────
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({"error": error.description}), error.code

    # ── 500 Catch-all ──────────────────────────────────────────
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Unhandled exception: %s", error)
        return jsonify({"error": "Internal server error"}), 500
