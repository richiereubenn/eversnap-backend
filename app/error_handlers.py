import logging
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from flask_limiter.errors import RateLimitExceeded

from app.shared.responses import api_response
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
from app.features.photos.exceptions import PhotoNotFoundError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Daftarkan semua error handler ke Flask app — satu tempat untuk semua."""

    # ── 422 Validation ─────────────────────────────────────────
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return api_response(422, "Validation error", {"errors": error.messages})

    # ── 401 Unauthorized ───────────────────────────────────────
    @app.errorhandler(InvalidCredentialsError)
    def handle_invalid_credentials(error):
        return api_response(401, str(error))

    # ── 409 Conflict ───────────────────────────────────────────
    @app.errorhandler(EmailAlreadyExistsError)
    def handle_email_exists(error):
        return api_response(409, str(error))

    @app.errorhandler(UsernameAlreadyTakenError)
    def handle_username_taken(error):
        return api_response(409, str(error))

    # ── 404 Not Found ──────────────────────────────────────────
    @app.errorhandler(UserNotFoundError)
    def handle_user_not_found(error):
        return api_response(404, str(error))

    @app.errorhandler(EventNotFoundError)
    def handle_event_not_found(error):
        return api_response(404, str(error))

    @app.errorhandler(QuestNotFoundError)
    def handle_quest_not_found(error):
        return api_response(404, str(error))

    @app.errorhandler(GuestNotFoundError)
    def handle_guest_not_found(error):
        return api_response(404, str(error))

    @app.errorhandler(GuestQuestNotFoundError)
    def handle_guest_quest_not_found(error):
        return api_response(404, str(error))

    @app.errorhandler(PhotoNotFoundError)
    def handle_photo_not_found(error):
        return api_response(404, str(error))

    # ── 403 Forbidden ──────────────────────────────────────────
    @app.errorhandler(EventStartedError)
    def handle_event_started(error):
        return api_response(403, str(error))


    # ── Flask HTTP exceptions (404, 405, etc.) ─────────────────
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return api_response(error.code, error.description)

    # ── 429 Too Many Requests (Rate Limit) ─────────────────────
    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(error):
        return api_response(
            429,
            "Too many requests. Please slow down.",
            {"limit": str(error.description)}
        )

    # ── 500 Catch-all ──────────────────────────────────────────
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Unhandled exception: %s", error)
        return api_response(500, "Internal server error")
