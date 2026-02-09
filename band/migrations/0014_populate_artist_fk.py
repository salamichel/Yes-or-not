from django.db import migrations


def populate_artist_fk(apps, schema_editor):
    Artist = apps.get_model("band", "Artist")
    Song = apps.get_model("band", "Song")

    for song in Song.objects.all():
        artist_obj, _ = Artist.objects.get_or_create(name=song.artist)
        song.artist_link = artist_obj
        song.save(update_fields=["artist_link"])


def reverse_artist_fk(apps, schema_editor):
    Song = apps.get_model("band", "Song")
    for song in Song.objects.filter(artist_link__isnull=False):
        song.artist = song.artist_link.name
        song.save(update_fields=["artist"])


class Migration(migrations.Migration):

    dependencies = [
        ("band", "0013_add_artist_model_and_song_artist_link"),
    ]

    operations = [
        migrations.RunPython(populate_artist_fk, reverse_artist_fk),
    ]
