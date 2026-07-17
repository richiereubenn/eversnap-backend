from app.extensions import ma
from app.features.guests.model import Guest
from marshmallow import fields, validate


class GuestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Guest
        load_instance = True
        exclude = ("event_id",)
        dump_only = ("id", "created_at")

    name = fields.String(required=True, validate=validate.Length(min=1, max=100))


guest_schema  = GuestSchema()
guests_schema = GuestSchema(many=True)
