from django.db import models
from django.utils import timezone


class SiteSettings(models.Model):
    band_name = models.CharField(max_length=200, default="Yes or Not")
    tagline = models.CharField(max_length=500, blank=True, default="Rock / Alternative")
    about_text = models.TextField(blank=True, verbose_name="Texte de présentation du groupe")
    hero_image = models.ImageField(upload_to="site/", blank=True, null=True, verbose_name="Image d'en-tête")
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    spotify_url = models.URLField(blank=True)
    email_contact = models.EmailField(blank=True, default="contact@yesornot.fr")

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.band_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Member(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    role = models.CharField(max_length=200, verbose_name="Rôle / Instrument")
    avatar = models.ImageField(upload_to="members/avatars/", blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name="Biographie")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        ordering = ["order", "last_name"]
        verbose_name = "Membre"
        verbose_name_plural = "Membres"

    def __str__(self):
        return f"{self.first_name} {self.last_name} – {self.role}"


class MemberPortfolioItem(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="portfolio_items")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="members/portfolio/", blank=True, null=True)
    video_url = models.URLField(blank=True, verbose_name="URL vidéo (YouTube, etc.)")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Élément de portfolio"
        verbose_name_plural = "Éléments de portfolio"

    def __str__(self):
        return f"{self.member} – {self.title}"


class Album(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    cover = models.ImageField(upload_to="albums/", blank=True, null=True, verbose_name="Pochette")
    release_date = models.DateField(verbose_name="Date de sortie")
    description = models.TextField(blank=True)
    spotify_url = models.URLField(blank=True, verbose_name="Lien Spotify")
    apple_music_url = models.URLField(blank=True, verbose_name="Lien Apple Music")
    deezer_url = models.URLField(blank=True, verbose_name="Lien Deezer")
    bandcamp_url = models.URLField(blank=True, verbose_name="Lien Bandcamp")

    class Meta:
        ordering = ["-release_date"]
        verbose_name = "Album"
        verbose_name_plural = "Albums"

    def __str__(self):
        return self.title


class Track(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="tracks")
    title = models.CharField(max_length=200, verbose_name="Titre")
    track_number = models.PositiveIntegerField(verbose_name="N° de piste")
    duration = models.CharField(max_length=10, blank=True, verbose_name="Durée (ex: 3:45)")

    class Meta:
        ordering = ["track_number"]
        verbose_name = "Piste"
        verbose_name_plural = "Pistes"

    def __str__(self):
        return f"{self.track_number}. {self.title}"


class Video(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    embed_url = models.URLField(verbose_name="URL d'intégration (embed)")
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="videos/", blank=True, null=True, verbose_name="Miniature")
    published_date = models.DateField(blank=True, null=True, verbose_name="Date de publication")
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-published_date"]
        verbose_name = "Vidéo"
        verbose_name_plural = "Vidéos"

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=300, verbose_name="Titre / Nom de l'événement")
    date = models.DateTimeField(verbose_name="Date et heure")
    venue = models.CharField(max_length=300, verbose_name="Lieu")
    city = models.CharField(max_length=200, verbose_name="Ville")
    description = models.TextField(blank=True)
    ticket_url = models.URLField(blank=True, verbose_name="Lien billetterie")
    poster = models.ImageField(upload_to="events/", blank=True, null=True, verbose_name="Affiche")
    is_cancelled = models.BooleanField(default=False, verbose_name="Annulé")

    class Meta:
        ordering = ["date"]
        verbose_name = "Événement / Date"
        verbose_name_plural = "Événements / Dates"

    def __str__(self):
        return f"{self.title} – {self.date:%d/%m/%Y}"

    @property
    def is_upcoming(self):
        return self.date >= timezone.now()


class ContactMessage(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=300, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    is_read = models.BooleanField(default=False, verbose_name="Lu")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.name} – {self.subject}"


class Page(models.Model):
    SLUG_CHOICES = [
        ("home", "Accueil"),
        ("about", "Le groupe"),
        ("members", "Membres"),
        ("albums", "Albums"),
        ("videos", "Vidéos"),
        ("events", "Dates"),
        ("contact", "Contact"),
    ]
    slug = models.SlugField(unique=True, choices=SLUG_CHOICES)
    title = models.CharField(max_length=200, verbose_name="Titre de la page")
    subtitle = models.CharField(max_length=500, blank=True, verbose_name="Sous-titre")
    content = models.TextField(blank=True, verbose_name="Contenu éditorial")
    banner_image = models.ImageField(upload_to="pages/", blank=True, null=True, verbose_name="Image bannière")

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return self.title
