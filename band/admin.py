from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteSettings, Member, MemberPortfolioItem, MemberPhoto, Album, Track,
    Video, Event, EventMedia, ContactMessage, Page,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Général", {"fields": ("band_name", "tagline", "about_text", "logo", "hero_image")}),
        ("Réseaux sociaux", {"fields": ("facebook_url", "instagram_url", "youtube_url", "spotify_url")}),
        ("Contact", {"fields": ("email_contact",)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class MemberPortfolioInline(admin.TabularInline):
    model = MemberPortfolioItem
    extra = 1


class MemberPhotoInline(admin.TabularInline):
    model = MemberPhoto
    extra = 3


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "role", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("first_name", "last_name", "role")
    inlines = [MemberPortfolioInline, MemberPhotoInline]


class TrackInline(admin.TabularInline):
    model = Track
    extra = 3


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date")
    search_fields = ("title",)
    inlines = [TrackInline]


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "video_type", "published_date", "is_featured", "order")
    list_editable = ("is_featured", "order")
    list_filter = ("is_featured",)
    search_fields = ("title",)
    fieldsets = (
        (None, {"fields": ("title", "description", "thumbnail", "published_date", "is_featured", "order")}),
        ("Source vidéo", {
            "description": "Remplir soit un lien embed YouTube, soit uploader un fichier MP4. Le fichier MP4 est prioritaire.",
            "fields": ("embed_url", "video_file"),
        }),
    )

    @admin.display(description="Type")
    def video_type(self, obj):
        return "MP4" if obj.is_mp4 else "Embed"


class EventMediaInline(admin.TabularInline):
    model = EventMedia
    extra = 0
    fields = ("media_type", "image", "video_file", "caption", "order", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="max-height:80px;border-radius:4px;">', obj.image.url)
        return "-"
    preview.short_description = "Aperçu"

    class Media:
        css = {"all": ("css/admin-dropzone.css",)}
        js = ("js/admin-dropzone.js",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "date", "venue", "city", "media_count", "is_cancelled")
    list_editable = ("is_cancelled",)
    list_filter = ("is_cancelled", "city")
    search_fields = ("title", "venue", "city")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [EventMediaInline]

    @admin.display(description="Médias")
    def media_count(self, obj):
        count = obj.media.count()
        return f"{count} média{'s' if count > 1 else ''}" if count else "-"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_editable = ("is_read",)
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")

    def has_add_permission(self, request):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title", "content")
    prepopulated_fields = {}


admin.site.site_header = "Yes or Not – Administration"
admin.site.site_title = "Yes or Not Admin"
admin.site.index_title = "Gestion du site"
