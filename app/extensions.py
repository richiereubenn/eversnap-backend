from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import redis
from rq import Queue

db      = SQLAlchemy()
jwt     = JWTManager()
migrate = Migrate()
ma      = Marshmallow()

# Diinisialisasi di create_app() menggunakan init_rq()
rq_queue: Queue | None = None


def init_rq(redis_url: str, queue_name: str) -> None:
    """Inisialisasi Redis Queue untuk background job processing."""
    global rq_queue
    conn      = redis.from_url(redis_url)
    rq_queue  = Queue(queue_name, connection=conn)
