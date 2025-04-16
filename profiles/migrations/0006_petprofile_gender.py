# Generated by Django 4.2.19 on 2025-04-16 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0005_alter_userprofile_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="petprofile",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("male", "Male"), ("female", "Female")],
                max_length=10,
                null=True,
            ),
        ),
    ]
