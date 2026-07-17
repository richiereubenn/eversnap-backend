from app.extensions import db
from datetime import datetime, timezone


class Photo(db.Model):
    __tablename__ = "photos"

    id              = db.Column(db.Integer, primary_key=True)
    guest_quest_id  = db.Column(db.Integer, db.ForeignKey("guest_quests.id"), nullable=False)
    url             = db.Column(db.String(300), nullable=False)
    file_size       = db.Column(db.Integer, nullable=True)
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    guest_quest = db.relationship("GuestQuest", back_populates="photos")

    def __repr__(self) -> str:
        return f"<Photo {self.id}>"
