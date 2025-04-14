# Generated by Django 4.2.19 on 2025-04-14 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0004_userprofile_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="location",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Brooklyn", "Brooklyn"),
                    ("Manhattan", "Manhattan"),
                    ("Queens", "Queens"),
                    ("Bronx", "Bronx"),
                    ("Staten Island", "Staten Island"),
                ],
                max_length=100,
                null=True,
            ),
        ),
    ]
