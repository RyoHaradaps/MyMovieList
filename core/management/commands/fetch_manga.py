from django.core.management.base import BaseCommand
from core.models import BaseContent
import requests

class Command(BaseCommand):
    help = "Fetch and import popular manga from Jikan API (MyAnimeList)"

    def handle(self, *args, **kwargs):
        url = "https://api.jikan.moe/v4/top/manga?page=1"
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
            year = item.get('published', {}).get('from', '')
            year = int(year.split('-')[0]) if year else 2000

            if not title:
                continue

            BaseContent.objects.update_or_create(
                title=title,
                content_type='comic',
                defaults={
                    'description': description,
                    'poster_url': poster or '',
                    'genre': 'Manga',
                    'rating': rating,
                    'release_year': year
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Manga imported successfully from Jikan API."))