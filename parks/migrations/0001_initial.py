# Generated by Django 5.1.6 on 2025-03-07 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DogRun',
            fields=[
                ('id', models.CharField(max_length=255)),
                ('prop_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('dogruns_type', models.CharField()),
                ('accessible', models.CharField(max_length=50)),
                ('notes', models.TextField(max_length=255)),
            ],
            options={
                'db_table': 'dog_runs',
            },
        ),
    ]
