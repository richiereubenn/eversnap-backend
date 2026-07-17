from app.extensions import ma
from app.features.auth.model import User
from marshmallow import fields, validate


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ("password_hash",)

    # Write-only: dipakai saat input, tidak di-serialize ke output
    password = fields.String(load_only=True, required=True, validate=validate.Length(min=6))
    email    = fields.Email(required=True)
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))


user_schema  = UserSchema()
users_schema = UserSchema(many=True)
