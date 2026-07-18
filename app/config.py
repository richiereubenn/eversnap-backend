import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # General
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    DEBUG = False

    # Database
    db_url = os.environ.get("DATABASE_URL", "sqlite:///eversnap.db")
    # SQLAlchemy 1.4+ deprecated postgres:// prefix in favor of postgresql://
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-production!!")
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # QR Codes
    QR_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "qr")

    # Base URL (used inside QR code link)
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

    # Redis
    REDIS_URL            = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    REDIS_EVENT_CACHE_TTL = int(os.environ.get("REDIS_EVENT_CACHE_TTL", 3600))  # 1 jam


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
