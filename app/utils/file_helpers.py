import os

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_upload(filename: str, file_size: int) -> str | None:
    """Dosya uzantısı ve boyut kontrolü. Hata varsa mesaj döner, yoksa None."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return "Sadece PDF dosyaları kabul edilmektedir."
    if file_size > MAX_FILE_SIZE:
        return "Dosya boyutu 10 MB'ı aşamaz."
    return None
