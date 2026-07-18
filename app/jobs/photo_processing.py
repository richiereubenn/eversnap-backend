"""
Background job untuk memproses foto yang diupload:
1. Kompres foto asli (kualitas lebih rendah untuk hemat storage)
2. Buat thumbnail (resize ke lebar THUMBNAIL_WIDTH px)
3. Update record Photo di DB (status=done, thumbnail_url terisi)

Fungsi ini dijalankan oleh RQ Worker di proses terpisah,
sehingga tidak memblokir thread Flask server utama.

PENTING: Fungsi ini TIDAK boleh menggunakan `current_app` karena
         berjalan di luar Flask request context. Flask app context
         dibuat secara manual menggunakan create_app().
"""
import os
import logging

from PIL import Image

logger = logging.getLogger(__name__)


def process_photo_job(photo_id: int, upload_folder: str, thumbnail_width: int, compress_quality: int, database_url: str) -> None:
    """
    RQ Job: Kompres foto asli dan buat thumbnail.

    Args:
        photo_id       : ID record Photo di database.
        upload_folder  : Path absolut ke folder uploads (dari config["UPLOAD_FOLDER"]).
        thumbnail_width: Lebar target thumbnail dalam piksel (contoh: 400).
        compress_quality: Kualitas kompresi JPEG/WebP (1-95, contoh: 85).
        database_url   : URL koneksi database untuk membuat Flask app context.
    """
    # ── Buat Flask app context secara manual ────────────────────────────────────
    # Diperlukan agar SQLAlchemy & model bisa digunakan di proses worker yang terpisah.
    from app import create_app
    from app.config import Config

    class WorkerConfig(Config):
        SQLALCHEMY_DATABASE_URI = database_url

    app = create_app(WorkerConfig)

    with app.app_context():
        from app.features.photos.model import Photo
        from app.extensions import db

        photo = db.session.get(Photo, photo_id)
        if not photo:
            logger.error(f"[PhotoJob] Photo ID {photo_id} tidak ditemukan di DB.")
            return

        original_abs_path = os.path.join(upload_folder, photo.url)
        if not os.path.exists(original_abs_path):
            logger.error(f"[PhotoJob] File foto tidak ditemukan: {original_abs_path}")
            photo.status = "failed"
            db.session.commit()
            return

        try:
            logger.info(f"[PhotoJob] Mulai proses foto ID {photo_id}: {original_abs_path}")

            with Image.open(original_abs_path) as img:
                # Konversi ke RGB agar kompatibel dengan format JPEG/WebP
                # (format PNG/GIF bisa memiliki mode RGBA atau P)
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                # ── 1. Simpan ulang foto asli dengan kompresi ───────────────
                # Simpan di subfolder original/ dengan format JPEG untuk efisiensi
                original_dir = os.path.join(upload_folder, "photos", "original")
                os.makedirs(original_dir, exist_ok=True)

                original_basename = os.path.basename(original_abs_path)
                # Ubah ekstensi ke .jpg
                original_name_no_ext = os.path.splitext(original_basename)[0]
                compressed_filename  = f"{original_name_no_ext}.jpg"
                compressed_abs_path  = os.path.join(original_dir, compressed_filename)

                img.save(compressed_abs_path, format="JPEG", quality=compress_quality, optimize=True)
                logger.info(f"[PhotoJob] Foto asli dikompres: {compressed_abs_path}")

                # ── 2. Buat Thumbnail ───────────────────────────────────────
                thumb_img = img.copy()

                # Hitung tinggi thumbnail secara proporsional
                orig_w, orig_h = thumb_img.size
                if orig_w > thumbnail_width:
                    ratio     = thumbnail_width / orig_w
                    thumb_h   = int(orig_h * ratio)
                    thumb_img = thumb_img.resize((thumbnail_width, thumb_h), Image.LANCZOS)

                thumb_dir = os.path.join(upload_folder, "photos", "thumbnails")
                os.makedirs(thumb_dir, exist_ok=True)

                thumb_filename = f"thumb_{original_name_no_ext}.jpg"
                thumb_abs_path = os.path.join(thumb_dir, thumb_filename)

                thumb_img.save(thumb_abs_path, format="JPEG", quality=compress_quality, optimize=True)
                logger.info(f"[PhotoJob] Thumbnail dibuat: {thumb_abs_path}")

            # ── 3. Update record Photo di DB ────────────────────────────────
            # Simpan path relatif terhadap upload_folder
            photo.thumbnail_url = f"photos/thumbnails/{thumb_filename}"
            photo.status        = "done"
            db.session.commit()

            logger.info(f"[PhotoJob] Selesai: Photo ID {photo_id} status=done, thumbnail={photo.thumbnail_url}")

        except Exception as e:
            logger.exception(f"[PhotoJob] Gagal memproses Photo ID {photo_id}: {e}")
            try:
                photo.status = "failed"
                db.session.commit()
            except Exception:
                pass
