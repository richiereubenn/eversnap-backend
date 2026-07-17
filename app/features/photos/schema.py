from app.extensions import ma
from app.features.photos.model import Photo
from marshmallow import fields
from flask import current_app


class PhotoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Photo
        load_instance = True
        exclude = ("guest_quest_id",)
        dump_only = ("id", "created_at")

    # Return full URL for the photo
    photo_url = fields.Method("get_photo_url", dump_only=True)

    def get_photo_url(self, obj: Photo):
        if obj.url:
            return f"{current_app.config['BASE_URL']}/uploads/{obj.url}"
        return None


photo_schema  = PhotoSchema()
photos_schema = PhotoSchema(many=True)
