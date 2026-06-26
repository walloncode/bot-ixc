"""OCR via Tesseract. Lê texto de screenshots. Isolado e sem efeitos colaterais."""
from __future__ import annotations

from config import settings


def read_text(image_path: str) -> str:
    """Extrai texto de uma imagem. Retorna string (vazia se falhar)."""
    import pytesseract
    from PIL import Image

    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    try:
        return pytesseract.image_to_string(Image.open(image_path), lang="por")
    except Exception:  # noqa: BLE001 - OCR é best-effort
        return ""
