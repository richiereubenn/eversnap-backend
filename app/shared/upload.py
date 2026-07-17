import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    """Return True jika extension file diizinkan."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file, subfolder: str, prefix: str = "") -> str | None:
    """
    Simpan file upload ke UPLOAD_FOLDER/<subfolder>/.
    Return path relatif (e.g. 'quests/event3_photo.jpg'), atau None jika tidak valid.
    """
    if not (file and file.filename and allowed_file(file.filename)):
        return None

    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    if prefix:
        filename = f"{prefix}_{filename}"

    file.save(os.path.join(upload_dir, filename))
    return f"{subfolder}/{filename}"
