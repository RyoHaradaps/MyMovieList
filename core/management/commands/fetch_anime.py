from django.core.management.base import BaseCommand
from core.models import BaseContent
import requests

class Command(BaseCommand):
    help = "Fetch and import popular anime from Jikan API (MyAnimeList)"

    def handle(self, *args, **kwargs):
        url = "https://api.jikan.moe/v4/top/anime?page=1"
        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to fetch data from Jikan API."))
            return

        data = response.json()

        for item in data.get('data', []):
            title = item.get('title')
            description = item.get('synopsis')
            poster = item.get('images', {}).get('jpg', {}).get('large_image_url')
            rating = item.get('score')
            year = item.get('year') or 2000  # fallback if year is missing

            if not title:
                continue

            BaseContent.objects.update_or_create(
                title=title,
                content_type='animatedshow',
                defaults={
                    'description': description,
                    'poster_url': poster or '',
                    'genre': 'Anime',
                    'rating': rating,
                    'release_year': year
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Anime imported successfully from Jikan API."))