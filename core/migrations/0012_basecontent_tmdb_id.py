# Generated by Django 5.2.3 on 2025-06-23 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_genre_remove_basecontent_genre_basecontent_genres'),
    ]

    operations = [
        migrations.AddField(
            model_name='basecontent',
            name='tmdb_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
