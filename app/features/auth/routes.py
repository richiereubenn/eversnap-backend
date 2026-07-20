from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from marshmallow import ValidationError

from app.extensions import limiter
from app.features.auth.schema import user_schema
from app.features.auth.service import AuthService
from app.shared.responses import api_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")   # Ketat: cegah spam pembuatan akun admin
def register():
    """POST /api/auth/register — Daftar akun admin baru."""
    data = request.get_json(silent=True) or {}

    # Validasi input — ValidationError ditangkap oleh global handler → 422
    user_schema.load(data)

    # Business logic — EmailAlreadyExistsError/UsernameAlreadyTakenError → 409
    user = AuthService.register(data)

    return api_response(201, "Account created successfully", {
        "user": user_schema.dump(user),
    })


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")  # Ketat: cegah brute-force tebak password
def login():
    """POST /api/auth/login — Login dan dapat JWT."""
    data     = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return api_response(400, "Email and password are required")

    # InvalidCredentialsError → ditangkap global handler → 401
    user = AuthService.authenticate(email, password)

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return api_response(200, "Login successful", {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "user":          user_schema.dump(user),
    })


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """POST /api/auth/refresh — Dapatkan access token baru dari refresh token."""
    user_id      = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return api_response(200, "Token refreshed successfully", {"access_token": access_token})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """GET /api/auth/me — Info user yang sedang login."""
    user_id = int(get_jwt_identity())
    user    = AuthService.get_or_404(user_id)  # UserNotFoundError → 404
    return api_response(200, "User info retrieved successfully", user_schema.dump(user))
