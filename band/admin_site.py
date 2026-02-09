from django.contrib.admin import AdminSite
from django.utils import timezone


class BandAdminSite(AdminSite):
    site_header = "Yes or Not – Administration"
    site_title = "Yes or Not Admin"
    index_title = "Tableau de bord"

    def each_context(self, request):
        context = super().each_context(request)
        # Lazy import to avoid circular imports
        from band.models import (
            Member, Album, Track, Video, Event, ContactMessage, Page,
        )

        now = timezone.now()
        upcoming_events = Event.objects.filter(date__gte=now, is_cancelled=False)
        past_events = Event.objects.filter(date__lt=now)
        unread_messages = ContactMessage.objects.filter(is_read=False)
        recent_messages = ContactMessage.objects.order_by("-created_at")[:5]
        next_event = upcoming_events.order_by("date").first()

        context["metrics"] = {
            "members_active": Member.objects.filter(is_active=True).count(),
            "members_total": Member.objects.count(),
            "albums_count": Album.objects.count(),
            "tracks_count": Track.objects.count(),
            "videos_count": Video.objects.count(),
            "events_upcoming": upcoming_events.count(),
            "events_past": past_events.count(),
            "events_cancelled": Event.objects.filter(is_cancelled=True).count(),
            "messages_unread": unread_messages.count(),
            "messages_total": ContactMessage.objects.count(),
            "pages_count": Page.objects.count(),
            "next_event": next_event,
            "recent_messages": recent_messages,
        }
        return context
