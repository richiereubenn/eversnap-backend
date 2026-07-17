from app.extensions import db
from datetime import datetime, timezone


class GuestQuest(db.Model):
    __tablename__ = "guest_quests"
    __table_args__ = (
        db.UniqueConstraint("guest_id", "quest_id", name="uq_guest_quest"),
    )

    id          = db.Column(db.Integer, primary_key=True)
    guest_id    = db.Column(db.Integer, db.ForeignKey("guests.id"), nullable=False)
    quest_id    = db.Column(db.Integer, db.ForeignKey("quests.id"), nullable=False)
    is_complete = db.Column(db.Boolean, default=False, nullable=False)
    message     = db.Column(db.Text, nullable=True)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    guest  = db.relationship("Guest", back_populates="guest_quests")
    quest  = db.relationship("Quest")
    photos = db.relationship("Photo", back_populates="guest_quest", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<GuestQuest guest={self.guest_id} quest={self.quest_id}>"
