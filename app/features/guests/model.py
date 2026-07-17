from app.extensions import db
from datetime import datetime, timezone


class Guest(db.Model):
    __tablename__ = "guests"

    id         = db.Column(db.Integer, primary_key=True)
    event_id   = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    name       = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    event        = db.relationship("Event", back_populates="guests")
    guest_quests = db.relationship("GuestQuest", back_populates="guest", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Guest {self.name}>"
