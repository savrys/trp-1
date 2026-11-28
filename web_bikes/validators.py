"""Валидаторы загружаемых файлов приложения web_bikes."""

from pathlib import Path

from django.core.exceptions import ValidationError

MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _read_header(image):
    """Прочитать первые байты файла и вернуть позицию чтения в начало."""
    try:
        image.seek(0)
    except (AttributeError, OSError):
        pass

    header = image.read(12)

    try:
        image.seek(0)
    except (AttributeError, OSError):
        pass

    return header


def validate_bike_image(image):
    """Проверить размер, расширение и сигнатуру изображения.

    Проверка не требует Pillow: формат определяется по первым байтам файла,
    поэтому переименованный текстовый файл не пройдёт валидацию.
    """
    if not image:
        return

    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            "Размер изображения не должен превышать 5 МБ.",
            code="image_too_large",
        )

    extension = Path(image.name).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            "Допустимы изображения форматов JPEG, PNG или WebP.",
            code="unsupported_image_format",
        )

    header = _read_header(image)

    is_png = header.startswith(b"\x89PNG\r\n\x1a\n")
    is_jpeg = header.startswith(b"\xff\xd8\xff")
    is_webp = (
        len(header) >= 12
        and header.startswith(b"RIFF")
        and header[8:12] == b"WEBP"
    )

    if not (is_png or is_jpeg or is_webp):
        raise ValidationError(
            "Файл не является изображением JPEG, PNG или WebP.",
            code="invalid_image_content",
        )
