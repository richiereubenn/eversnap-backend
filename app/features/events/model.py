from app.extensions import db
from datetime import datetime, timezone


class Event(db.Model):
    __tablename__ = "events"

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name         = db.Column(db.String(150), nullable=False)
    event_type   = db.Column(db.String(20), nullable=False)   # 'wedding' | 'sweet17' | 'other'
    date         = db.Column(db.Date, nullable=True)
    location     = db.Column(db.String(200), nullable=True)
    description  = db.Column(db.Text, nullable=True)
    qr_code_path = db.Column(db.String(300), nullable=True)
    expired_date = db.Column(db.DateTime, nullable=True)
    start_date   = db.Column(db.DateTime, nullable=True)
    need_redeem  = db.Column(db.Boolean, nullable=True)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at   = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # String-based relationships untuk hindari circular import antar feature
    user   = db.relationship("User", back_populates="events")
    quests = db.relationship("Quest", back_populates="event", cascade="all, delete-orphan")
    guests = db.relationship("Guest", back_populates="event", cascade="all, delete-orphan")

    @property
    def quest_count(self) -> int:
        return len(self.quests)

    def __repr__(self) -> str:
        return f"<Event {self.name}>"
