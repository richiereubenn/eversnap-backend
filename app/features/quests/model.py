from app.extensions import db
from datetime import datetime, timezone


class Quest(db.Model):
    __tablename__ = "quests"

    id                 = db.Column(db.Integer, primary_key=True)
    event_id           = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    title              = db.Column(db.String(150), nullable=False)
    order_number    = db.Column(db.Integer, default=0)
    is_active       = db.Column(db.Boolean, default=True, nullable=False)
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at      = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # String-based relationship untuk hindari circular import antar feature
    event = db.relationship("Event", back_populates="quests")

    def __repr__(self) -> str:
        return f"<Quest {self.title}>"
