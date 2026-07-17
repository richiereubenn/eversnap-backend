from app.extensions import ma
from app.features.guest_quests.model import GuestQuest
from marshmallow import fields


class GuestQuestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GuestQuest
        load_instance = True
        exclude = ("guest_id", "quest_id")
        dump_only = ("id", "created_at", "updated_at")

    # Nested quest info for richer output
    quest_title = fields.Method("get_quest_title", dump_only=True)
    photos      = fields.Method("get_photos", dump_only=True)

    def get_quest_title(self, obj: GuestQuest):
        return obj.quest.title if obj.quest else None

    def get_photos(self, obj: GuestQuest):
        from app.features.photos.schema import photo_schema
        return [photo_schema.dump(p) for p in obj.photos]


guest_quest_schema  = GuestQuestSchema()
guest_quests_schema = GuestQuestSchema(many=True)
