import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("band", "0014_populate_artist_fk"),
    ]

    operations = [
        # Remove unique_together that references the old CharField artist
        migrations.AlterUniqueTogether(
            name="song",
            unique_together=set(),
        ),
        # Remove the old CharField artist
        migrations.RemoveField(
            model_name="song",
            name="artist",
        ),
        # Rename artist_link to artist
        migrations.RenameField(
            model_name="song",
            old_name="artist_link",
            new_name="artist",
        ),
        # Make the FK non-nullable
        migrations.AlterField(
            model_name="song",
            name="artist",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="songs",
                to="band.artist",
                verbose_name="Artiste",
            ),
        ),
        # Restore unique_together with the FK field
        migrations.AlterUniqueTogether(
            name="song",
            unique_together={("title", "artist")},
        ),
        # Update ordering
        migrations.AlterModelOptions(
            name="song",
            options={
                "ordering": ["artist__name", "title"],
                "verbose_name": "Morceau (répertoire)",
                "verbose_name_plural": "Morceaux (répertoire)",
            },
        ),
    ]
