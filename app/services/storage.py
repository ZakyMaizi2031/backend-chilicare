import os
import uuid
from ..core.config import settings

def save_image(file):
    """Simpan upload gambar ke filesystem dan kembalikan URL untuk disimpan di DB."""
    # Pastikan folder upload ada
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(settings.UPLOAD_DIR):
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
    execution = file.filename.split(".")[-1]
    unique_filename = f"chili_{uuid.uuid4().hex}.{execution}"

    # Ekstrak ekstensi file
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
    unique_filename = f"chili_{uuid.uuid4().hex}.{file_ext}"

    # Path filesystem untuk menyimpan file
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Tulis ke disk
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Return URL yang cocok untuk StaticFiles mount dengan forward slash agar bisa diakses via HTTP
    # Ubah backslash menjadi forward slash untuk URL web
    return f"static/uploads/{unique_filename}"

# Alias untuk kompatibilitas dengan detection.py
def save_upload_file(file):
    """Wrapper untuk save_image - untuk kompatibilitas dengan detection.py"""
    return save_image(file)
