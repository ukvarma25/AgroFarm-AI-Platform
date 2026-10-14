from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from backend.app.config import settings

ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def save_farm_image(farm_id: int, file: UploadFile) -> Path:
    suffix = Path(file.filename or "upload.jpg").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail="Only jpg/png/webp images are allowed")
    folder = settings.uploads_dir / str(farm_id)
    folder.mkdir(parents=True, exist_ok=True)
    stem = Path(file.filename or "image").stem.replace(" ", "_")[:40]
    dest = folder / f"{stem}_{uuid4().hex[:8]}{suffix}"
    dest.write_bytes(file.file.read())
    return dest
