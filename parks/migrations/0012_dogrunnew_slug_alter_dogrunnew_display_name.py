# Generated by Django 4.2.19 on 2025-04-07 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parks", "0011_dogrunnew_display_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="dogrunnew",
            name="slug",
            field=models.SlugField(null=True),
        ),
        migrations.AlterField(
            model_name="dogrunnew",
            name="display_name",
            field=models.TextField(),
        ),
    ]
