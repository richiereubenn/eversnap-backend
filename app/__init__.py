from flask import Flask
from app.extensions import db, jwt, migrate, ma, limiter, init_rq
from app.config import Config
import os



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Pastikan folder uploads ada
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    limiter.init_app(app)  # Rate limiter menggunakan Redis sebagai storage

    # Init RQ (Redis Queue) untuk background job processing
    try:
        init_rq(app.config["REDIS_URL"], app.config["RQ_QUEUE_NAME"])
    except Exception as e:
        app.logger.warning(f"[RQ] Failed to connect to Redis for job queue: {e}")

    # Import semua model agar SQLAlchemy mendaftarkannya sebelum dipakai
    from app.features.auth.model import User       # noqa: F401
    from app.features.events.model import Event    # noqa: F401
    from app.features.quests.model import Quest    # noqa: F401
    from app.features.guests.model import Guest             # noqa: F401
    from app.features.guest_quests.model import GuestQuest  # noqa: F401
    from app.features.photos.model import Photo              # noqa: F401

    # Register blueprints dari feature folders
    from app.features.auth.routes import auth_bp
    from app.features.events.routes import events_bp
    from app.features.quests.routes import quests_bp
    from app.features.guests.routes import guests_bp
    from app.features.photos.routes import photos_bp

    app.register_blueprint(auth_bp,    url_prefix="/api/auth")
    app.register_blueprint(events_bp,  url_prefix="/api/events")
    app.register_blueprint(quests_bp,  url_prefix="/api/events")
    app.register_blueprint(guests_bp,  url_prefix="/api/guest")
    app.register_blueprint(photos_bp,  url_prefix="/api/events")  # SSE: /api/events/<id>/live

    # Register global error handlers
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Route untuk menyajikan file uploads saat development (tanpa Nginx)
    from flask import send_from_directory
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Tambahkan header instance untuk memantau load balancing
    import socket
    @app.after_request
    def add_instance_header(response):
        response.headers["X-Handled-By"] = socket.gethostname()
        return response

    return app
