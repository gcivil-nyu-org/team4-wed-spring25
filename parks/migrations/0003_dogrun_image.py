# Generated by Django 2.2 on 2025-03-10 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parks", "0002_auto_20250310_0644"),
    ]

    operations = [
        migrations.AddField(
            model_name="dogrun",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="dogruns/"),
        ),
    ]