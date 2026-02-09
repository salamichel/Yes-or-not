from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

from band.images import optimize_image


class SiteSettings(models.Model):
    band_name = models.CharField(max_length=200, default="Yes or Not")
    tagline = models.CharField(max_length=500, blank=True, default="Rock / Alternative")
    about_text = CKEditor5Field(blank=True, verbose_name="Texte de présentation du groupe", config_name="default")
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
        optimize_image(self.hero_image)
        optimize_image(self.logo, max_dimension=512)
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Member(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, blank=True, default="", verbose_name="Nom")
    role = models.CharField(max_length=200, verbose_name="Rôle / Instrument")
    avatar = models.ImageField(upload_to="members/avatars/", blank=True, null=True)
    bio = CKEditor5Field(blank=True, verbose_name="Biographie", config_name="default")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        ordering = ["order", "first_name"]
        verbose_name = "Membre"
        verbose_name_plural = "Membres"

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return f"{name} – {self.role}"

    def save(self, *args, **kwargs):
        optimize_image(self.avatar, max_dimension=800)
        super().save(*args, **kwargs)


class MemberPortfolioItem(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="portfolio_items")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = CKEditor5Field(blank=True, config_name="default")
    image = models.ImageField(upload_to="members/portfolio/", blank=True, null=True)
    video_url = models.URLField(blank=True, verbose_name="URL vidéo (YouTube, etc.)")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Élément de portfolio"
        verbose_name_plural = "Éléments de portfolio"

    def __str__(self):
        return f"{self.member} – {self.title}"

    def save(self, *args, **kwargs):
        optimize_image(self.image)
        super().save(*args, **kwargs)


class MemberPhoto(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="members/gallery/", verbose_name="Photo")
    caption = models.CharField(max_length=300, blank=True, verbose_name="Légende")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        ordering = ["order"]
        verbose_name = "Photo"
        verbose_name_plural = "Galerie photos"

    def __str__(self):
        return self.caption or f"Photo {self.pk}"

    def save(self, *args, **kwargs):
        optimize_image(self.image)
        super().save(*args, **kwargs)


class Album(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    cover = models.ImageField(upload_to="albums/", blank=True, null=True, verbose_name="Pochette")
    release_date = models.DateField(verbose_name="Date de sortie")
    description = CKEditor5Field(blank=True, config_name="default")
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

    def save(self, *args, **kwargs):
        optimize_image(self.cover)
        super().save(*args, **kwargs)


class Track(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="tracks")
    title = models.CharField(max_length=200, verbose_name="Titre")
    track_number = models.PositiveIntegerField(verbose_name="N° de piste")
    duration = models.CharField(max_length=10, blank=True, verbose_name="Durée (ex: 3:45)")
    audio_file = models.FileField(upload_to="albums/tracks/", blank=True, null=True, verbose_name="Fichier audio (MP3)")

    class Meta:
        ordering = ["track_number"]
        verbose_name = "Piste"
        verbose_name_plural = "Pistes"

    def __str__(self):
        return f"{self.track_number}. {self.title}"


class Video(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    embed_url = models.URLField(blank=True, verbose_name="URL d'intégration (embed YouTube)")
    video_file = models.FileField(
        upload_to="videos/mp4/", blank=True, null=True,
        verbose_name="Fichier vidéo (MP4)",
        help_text="Télécharger un fichier MP4. Si rempli, sera utilisé à la place du lien embed.",
    )
    description = CKEditor5Field(blank=True, config_name="default")
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

    def save(self, *args, **kwargs):
        optimize_image(self.thumbnail, max_dimension=1280)
        super().save(*args, **kwargs)

    @property
    def is_mp4(self):
        return bool(self.video_file)


class Event(models.Model):
    title = models.CharField(max_length=300, verbose_name="Titre / Nom de l'événement")
    slug = models.SlugField(max_length=350, unique=True, blank=True, verbose_name="Slug URL",
                            help_text="Généré automatiquement à partir du titre. Modifiable.")
    date = models.DateTimeField(verbose_name="Date et heure")
    venue = models.CharField(max_length=300, verbose_name="Lieu")
    city = models.CharField(max_length=200, verbose_name="Ville")
    description = CKEditor5Field(blank=True, config_name="default")
    ticket_url = models.URLField(blank=True, verbose_name="Lien billetterie")
    poster = models.ImageField(upload_to="events/", blank=True, null=True, verbose_name="Affiche")
    is_cancelled = models.BooleanField(default=False, verbose_name="Annulé")

    class Meta:
        ordering = ["date"]
        verbose_name = "Événement / Date"
        verbose_name_plural = "Événements / Dates"

    def __str__(self):
        return f"{self.title} – {self.date:%d/%m/%Y}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "evenement"
            slug = base_slug
            n = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        optimize_image(self.poster)
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        return self.date >= timezone.now()


class EventMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("photo", "Photo"),
        ("video", "Vidéo"),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default="photo", verbose_name="Type")
    image = models.ImageField(upload_to="events/gallery/", blank=True, null=True, verbose_name="Photo")
    video_file = models.FileField(upload_to="events/gallery/videos/", blank=True, null=True, verbose_name="Fichier vidéo (MP4)")
    caption = models.CharField(max_length=300, blank=True, verbose_name="Légende")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        ordering = ["order"]
        verbose_name = "Média de l'événement"
        verbose_name_plural = "Galerie média"

    def __str__(self):
        return self.caption or f"{self.get_media_type_display()} {self.pk}"


class Song(models.Model):
    title = models.CharField(max_length=300, verbose_name="Titre")
    artist = models.CharField(max_length=300, verbose_name="Artiste")
    youtube_url = models.URLField(blank=True, verbose_name="URL YouTube")
    audio_file = models.FileField(
        upload_to="songs/mp3/", blank=True, null=True,
        verbose_name="Enregistrement MP3",
        help_text="Fichier MP3 du morceau",
    )
    lyrics = models.TextField(blank=True, verbose_name="Paroles")
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        ordering = ["artist", "title"]
        verbose_name = "Morceau (répertoire)"
        verbose_name_plural = "Morceaux (répertoire)"
        unique_together = [("title", "artist")]

    def __str__(self):
        return f"{self.artist} – {self.title}"


class SheetMusic(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="sheets")
    instrument = models.CharField(max_length=200, verbose_name="Instrument")
    file = models.FileField(
        upload_to="songs/sheets/",
        verbose_name="Fichier (PDF, image…)",
        help_text="Partition au format PDF ou image",
    )

    class Meta:
        ordering = ["instrument"]
        verbose_name = "Partition"
        verbose_name_plural = "Partitions"
        unique_together = [("song", "instrument")]

    def __str__(self):
        return f"{self.song.title} – {self.instrument}"


class SetlistEntry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="setlist_entries")
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="setlist_entries")
    position = models.PositiveIntegerField(verbose_name="Ordre de passage")

    class Meta:
        ordering = ["position"]
        verbose_name = "Morceau de la setlist"
        verbose_name_plural = "Setlist"
        unique_together = [("event", "song"), ("event", "position")]

    def __str__(self):
        return f"{self.position}. {self.song}"


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
    content = CKEditor5Field(blank=True, verbose_name="Contenu éditorial", config_name="default")
    banner_image = models.ImageField(upload_to="pages/", blank=True, null=True, verbose_name="Image bannière")

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        optimize_image(self.banner_image)
        super().save(*args, **kwargs)
