"""Image optimization utilities for the band app."""

import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image

# Max dimension for uploaded images (width or height)
MAX_DIMENSION = 1920
JPEG_QUALITY = 85


def optimize_image(image_field, max_dimension=MAX_DIMENSION):
    """Resize an image if it exceeds max_dimension and optimize quality.

    Works with Django ImageField/FieldFile. Should be called in model.save().
    Returns True if the image was modified, False otherwise.
    """
    if not image_field:
        return False

    try:
        image_field.seek(0)
        img = Image.open(image_field)
    except Exception:
        return False

    original_format = img.format or "JPEG"
    width, height = img.size
    modified = False

    # Resize if either dimension exceeds the limit
    if width > max_dimension or height > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
        modified = True

    # Always re-save to optimize quality (strip metadata, optimize)
    if not modified and original_format.upper() in ("JPEG", "JPG"):
        modified = True  # Re-save to optimize

    if modified:
        buffer = BytesIO()
        if img.mode in ("RGBA", "P") and original_format.upper() == "PNG":
            img.save(buffer, format="PNG", optimize=True)
        else:
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)

            # Change extension to .jpg if it was something else
            name = image_field.name
            base, ext = os.path.splitext(name)
            if ext.lower() not in (".jpg", ".jpeg"):
                image_field.name = base + ".jpg"

        buffer.seek(0)
        image_field.save(image_field.name, ContentFile(buffer.read()), save=False)
        return True

    return False
