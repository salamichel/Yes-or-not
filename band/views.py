from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from .models import SiteSettings, Member, Album, Video, Event, ContactMessage, Page


def get_page(slug):
    try:
        return Page.objects.get(slug=slug)
    except Page.DoesNotExist:
        return None


def get_context(slug=None):
    ctx = {"settings": SiteSettings.load()}
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
            messages.success(request, "Votre message a bien été envoyé. Merci !")
            return redirect("contact")
        else:
            messages.error(request, "Veuillez remplir tous les champs.")

    return render(request, "band/contact.html", ctx)
