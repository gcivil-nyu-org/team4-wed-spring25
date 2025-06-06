# Generated by Django 4.2.19 on 2025-04-15 04:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("parks", "0014_parkimage_review"),
    ]

    operations = [
        migrations.CreateModel(
            name="ParkPresence",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Current", "Current"),
                            ("On their way", "On their way"),
                        ],
                        max_length=20,
                    ),
                ),
                ("time", models.DateTimeField(blank=True, null=True)),
                ("checked_in_at", models.DateTimeField(auto_now_add=True)),
                (
                    "park",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="presences",
                        to="parks.dogrunnew",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="park_presences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "park_presence",
                "ordering": ["-checked_in_at"],
                "unique_together": {("user", "park")},
            },
        ),
    ]
