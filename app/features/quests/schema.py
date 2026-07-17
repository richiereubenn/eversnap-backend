from app.extensions import ma
from app.features.quests.model import Quest
from marshmallow import fields, validate


class QuestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Quest
        load_instance = True
        exclude = ("event_id",)
        dump_only = ("id", "created_at", "updated_at")

    title           = fields.String(required=True, validate=validate.Length(min=1, max=150))
    is_active       = fields.Boolean(load_default=True)
    order_number    = fields.Integer(load_default=0)


quest_schema  = QuestSchema()
quests_schema = QuestSchema(many=True)
