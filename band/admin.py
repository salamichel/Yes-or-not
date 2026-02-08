from django.contrib import admin
from .models import (
    SiteSettings, Member, MemberPortfolioItem, Album, Track,
    Video, Event, ContactMessage, Page,
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


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "role", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("first_name", "last_name", "role")
    inlines = [MemberPortfolioInline]


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
    list_display = ("title", "published_date", "is_featured", "order")
    list_editable = ("is_featured", "order")
    list_filter = ("is_featured",)
    search_fields = ("title",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "venue", "city", "is_cancelled")
    list_editable = ("is_cancelled",)
    list_filter = ("is_cancelled", "city")
    search_fields = ("title", "venue", "city")


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
