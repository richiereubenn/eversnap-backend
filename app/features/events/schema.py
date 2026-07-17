from app.extensions import ma
from app.features.events.model import Event
from marshmallow import fields, validate


class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True
        exclude = ("user_id",)
        dump_only = ("id", "created_at", "updated_at", "qr_code_path")

    name       = fields.String(required=True, validate=validate.Length(min=1, max=150))
    event_type = fields.String(
        required=True,
        validate=validate.OneOf(["wedding", "sweet17", "other"]),
    )
    date       = fields.Date(allow_none=True)
    start_date = fields.DateTime(allow_none=True)

    # Computed fields
    quest_count = fields.Integer(dump_only=True)
    qr_url      = fields.Method("get_qr_url", dump_only=True)

    def get_qr_url(self, obj: Event):
        if obj.qr_code_path:
            from flask import current_app
            return f"{current_app.config['BASE_URL']}/uploads/{obj.qr_code_path}"
        return None


event_schema  = EventSchema()
events_schema = EventSchema(many=True)
