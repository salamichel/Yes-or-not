"""Management command to optimize all existing images and generate thumbnails."""

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image

from band.images import optimize_image
from band.models import (
    Album,
    Event,
    Member,
    MemberPhoto,
    MemberPortfolioItem,
    Page,
    SiteSettings,
    Video,
)

# (Model, field_name, max_dimension)
IMAGE_FIELDS = [
    (SiteSettings, "hero_image", 1920),
    (SiteSettings, "logo", 512),
    (Member, "avatar", 800),
    (MemberPortfolioItem, "image", 1920),
    (MemberPhoto, "image", 1920),
    (Album, "cover", 1920),
    (Video, "thumbnail", 1280),
    (Event, "poster", 1920),
    (Page, "banner_image", 1920),
]

# Thumbnail specs: (Model, field_name, size)
THUMBNAIL_SPECS = [
    (Member, "avatar", "400x400"),
    (MemberPortfolioItem, "image", "600x400"),
    (MemberPhoto, "image", "400x400"),
    (Album, "cover", "400x400"),
    (Video, "thumbnail", "640x360"),
    (Event, "poster", "400x500"),
]


class Command(BaseCommand):
    help = "Optimize all existing images and pre-generate thumbnails"

    def add_arguments(self, parser):
        parser.add_argument(
            "--thumbnails-only",
            action="store_true",
            help="Only generate thumbnails, skip original optimization",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        thumbnails_only = options["thumbnails_only"]

        if not thumbnails_only:
            self._optimize_originals(dry_run)

        self._generate_thumbnails(dry_run)

    def _optimize_originals(self, dry_run):
        self.stdout.write(self.style.MIGRATE_HEADING("Optimizing original images..."))
        optimized = 0
        skipped = 0

        for model_class, field_name, max_dim in IMAGE_FIELDS:
            for obj in model_class.objects.all():
                image_field = getattr(obj, field_name)
                if not image_field:
                    continue

                try:
                    path = image_field.path
                    if not os.path.isfile(path):
                        continue
                except Exception:
                    continue

                # Check if image needs optimization
                try:
                    with Image.open(path) as img:
                        w, h = img.size
                        needs_resize = w > max_dim or h > max_dim
                        is_jpeg = img.format in ("JPEG", "JPG")
                except Exception:
                    continue

                if not needs_resize and not is_jpeg:
                    skipped += 1
                    continue

                label = f"{model_class.__name__}.{field_name} (pk={obj.pk})"
                if dry_run:
                    size_kb = os.path.getsize(path) // 1024
                    self.stdout.write(f"  Would optimize: {label} ({w}x{h}, {size_kb}KB)")
                else:
                    size_before = os.path.getsize(path)
                    if optimize_image(image_field, max_dimension=max_dim):
                        obj.save()
                        size_after = os.path.getsize(image_field.path)
                        saved = size_before - size_after
                        self.stdout.write(f"  Optimized: {label} (saved {saved // 1024}KB)")
                        optimized += 1
                    else:
                        skipped += 1

        self.stdout.write(
            self.style.SUCCESS(f"  Done: {optimized} optimized, {skipped} skipped")
        )

    def _generate_thumbnails(self, dry_run):
        from band.templatetags.thumbnails import thumbnail as make_thumbnail

        self.stdout.write(self.style.MIGRATE_HEADING("Generating thumbnails..."))
        generated = 0

        for model_class, field_name, size in THUMBNAIL_SPECS:
            for obj in model_class.objects.all():
                image_field = getattr(obj, field_name)
                if not image_field:
                    continue

                try:
                    if not os.path.isfile(image_field.path):
                        continue
                except Exception:
                    continue

                label = f"{model_class.__name__}.{field_name} (pk={obj.pk})"
                if dry_run:
                    self.stdout.write(f"  Would generate thumbnail: {label} @ {size}")
                else:
                    url = make_thumbnail(image_field, size)
                    if url and url != image_field.url:
                        self.stdout.write(f"  Generated: {label} @ {size}")
                        generated += 1

        self.stdout.write(self.style.SUCCESS(f"  Done: {generated} thumbnails generated"))
