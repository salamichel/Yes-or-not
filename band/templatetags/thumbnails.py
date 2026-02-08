import os
import hashlib

from django import template
from django.conf import settings
from PIL import Image

register = template.Library()

THUMBS_DIR = "thumbs"


@register.filter
def thumbnail(image_field, size="400x400"):
    """Generate a thumbnail for an ImageField and return its URL.

    Usage: {{ member.avatar|thumbnail:"400x400" }}

    Thumbnails are cached in MEDIA_ROOT/thumbs/ with a hash-based filename.
    """
    if not image_field:
        return ""

    try:
        width, height = (int(d) for d in size.split("x"))
    except (ValueError, AttributeError):
        return image_field.url

    source_path = image_field.path
    if not os.path.isfile(source_path):
        return image_field.url

    # Build a deterministic thumbnail path
    name_hash = hashlib.md5(
        f"{image_field.name}_{size}".encode()
    ).hexdigest()[:12]
    base, ext = os.path.splitext(image_field.name)
    # Use .webp for thumbnails to save bandwidth
    thumb_filename = f"{os.path.basename(base)}_{name_hash}.webp"
    thumb_rel_path = os.path.join(THUMBS_DIR, thumb_filename)
    thumb_abs_path = os.path.join(settings.MEDIA_ROOT, thumb_rel_path)

    # Return cached thumbnail if it exists and is newer than the source
    if os.path.isfile(thumb_abs_path):
        if os.path.getmtime(thumb_abs_path) >= os.path.getmtime(source_path):
            return settings.MEDIA_URL + thumb_rel_path

    # Generate thumbnail
    try:
        os.makedirs(os.path.dirname(thumb_abs_path), exist_ok=True)
        with Image.open(source_path) as img:
            img = _fix_orientation(img)
            img.thumbnail((width, height), Image.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
                img.save(thumb_abs_path, "WEBP", quality=82)
            else:
                img = img.convert("RGB")
                img.save(thumb_abs_path, "WEBP", quality=82)
        return settings.MEDIA_URL + thumb_rel_path
    except Exception:
        return image_field.url


def _fix_orientation(img):
    """Apply EXIF orientation tag and strip it."""
    try:
        from PIL import ExifTags

        for key, val in ExifTags.TAGS.items():
            if val == "Orientation":
                orientation_key = key
                break
        else:
            return img

        exif = img.getexif()
        orientation = exif.get(orientation_key)
        if orientation == 3:
            img = img.rotate(180, expand=True)
        elif orientation == 6:
            img = img.rotate(270, expand=True)
        elif orientation == 8:
            img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img
