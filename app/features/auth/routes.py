from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from marshmallow import ValidationError

from app.features.auth.schema import user_schema
from app.features.auth.service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """POST /api/auth/register — Daftar akun admin baru."""
    data = request.get_json(silent=True) or {}

    # Validasi input — ValidationError ditangkap oleh global handler → 422
    user_schema.load(data)

    # Business logic — EmailAlreadyExistsError/UsernameAlreadyTakenError → 409
    user = AuthService.register(data)

    return jsonify({
        "message": "Account created successfully",
        "user":    user_schema.dump(user),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/auth/login — Login dan dapat JWT."""
    data     = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # InvalidCredentialsError → ditangkap global handler → 401
    user = AuthService.authenticate(email, password)

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "user":          user_schema.dump(user),
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """POST /api/auth/refresh — Dapatkan access token baru dari refresh token."""
    user_id      = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """GET /api/auth/me — Info user yang sedang login."""
    user_id = int(get_jwt_identity())
    user    = AuthService.get_or_404(user_id)  # UserNotFoundError → 404
    return jsonify(user_schema.dump(user)), 200
