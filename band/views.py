import logging

import requests as http_requests
from django.conf import settings as django_settings
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from .models import SiteSettings, Member, Album, Video, Event, EventMedia, ContactMessage, Page

logger = logging.getLogger(__name__)


def get_page(slug):
    try:
        return Page.objects.get(slug=slug)
    except Page.DoesNotExist:
        return None


def get_context(slug=None):
    ctx = {"settings": SiteSettings.load()}
    ctx["has_albums"] = Album.objects.exists()
    ctx["has_videos"] = Video.objects.exists()
    if slug:
        ctx["page"] = get_page(slug)
    return ctx


def home(request):
    ctx = get_context("home")
    ctx["upcoming_events"] = Event.objects.filter(date__gte=timezone.now(), is_cancelled=False)[:3]
    ctx["featured_videos"] = Video.objects.filter(is_featured=True)[:2]
    ctx["albums"] = Album.objects.all()[:3]
    ctx["members"] = Member.objects.filter(is_active=True)
    return render(request, "band/home.html", ctx)


def about(request):
    ctx = get_context("about")
    ctx["members"] = Member.objects.filter(is_active=True)
    return render(request, "band/about.html", ctx)


def members_list(request):
    ctx = get_context("members")
    ctx["members"] = Member.objects.filter(is_active=True)
    return render(request, "band/members.html", ctx)


def member_detail(request, pk):
    ctx = get_context("members")
    ctx["member"] = get_object_or_404(Member, pk=pk, is_active=True)
    return render(request, "band/member_detail.html", ctx)


def albums_list(request):
    ctx = get_context("albums")
    ctx["albums"] = Album.objects.all()
    return render(request, "band/albums.html", ctx)


def album_detail(request, pk):
    ctx = get_context("albums")
    ctx["album"] = get_object_or_404(Album, pk=pk)
    return render(request, "band/album_detail.html", ctx)


def videos_list(request):
    ctx = get_context("videos")
    ctx["videos"] = Video.objects.all()
    return render(request, "band/videos.html", ctx)


def events_list(request):
    ctx = get_context("events")
    now = timezone.now()
    ctx["upcoming_events"] = Event.objects.filter(date__gte=now)
    ctx["past_events"] = Event.objects.filter(date__lt=now).order_by("-date")
    return render(request, "band/events.html", ctx)


def event_detail(request, slug):
    ctx = get_context("events")
    ctx["event"] = get_object_or_404(Event, slug=slug)
    ctx["photos"] = ctx["event"].media.filter(media_type="photo")
    ctx["videos"] = ctx["event"].media.filter(media_type="video")
    return render(request, "band/event_detail.html", ctx)


def _send_brevo_email(name, email, subject, message_text):
    """Send contact notification via Brevo transactional email API."""
    api_key = django_settings.BREVO_API_KEY
    if not api_key:
        logger.warning("BREVO_API_KEY not configured – email not sent")
        return False

    payload = {
        "sender": {
            "name": django_settings.BREVO_SENDER_NAME,
            "email": django_settings.BREVO_SENDER_EMAIL,
        },
        "to": [{"email": django_settings.BREVO_RECIPIENT_EMAIL}],
        "replyTo": {"email": email, "name": name},
        "subject": f"[Contact Yes or Not] {subject}",
        "htmlContent": (
            f"<h2>Nouveau message de contact</h2>"
            f"<p><strong>Nom :</strong> {name}</p>"
            f"<p><strong>Email :</strong> {email}</p>"
            f"<p><strong>Sujet :</strong> {subject}</p>"
            f"<hr>"
            f"<p>{message_text.replace(chr(10), '<br>')}</p>"
        ),
    }

    try:
        resp = http_requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=10,
        )
        if resp.status_code in (200, 201):
            return True
        logger.error("Brevo API error %s: %s", resp.status_code, resp.text)
        return False
    except http_requests.RequestException as exc:
        logger.error("Brevo API request failed: %s", exc)
        return False


def contact(request):
    ctx = get_context("contact")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        if name and email and subject and message_text:
            ContactMessage.objects.create(
                name=name, email=email, subject=subject, message=message_text,
            )
            _send_brevo_email(name, email, subject, message_text)
            messages.success(request, "Votre message a bien été envoyé. Merci !")
            return redirect("contact")
        else:
            messages.error(request, "Veuillez remplir tous les champs.")

    return render(request, "band/contact.html", ctx)
