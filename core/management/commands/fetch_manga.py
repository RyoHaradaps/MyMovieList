from django.core.management.base import BaseCommand
from core.models import BaseContent, Genre
import requests

class Command(BaseCommand):
    help = "Fetch and import popular manga from Jikan API (MyAnimeList)"

    def handle(self, *args, **kwargs):
        url = "https://api.jikan.moe/v4/top/manga?type=manga&limit=25"
        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to fetch data from Jikan API."))
            return
        data = response.json()
        for item in data.get('data', []):
            title = item.get('title')
            description = item.get('synopsis') or "No description available."
            poster = item.get('images', {}).get('jpg', {}).get('large_image_url') or item.get('images', {}).get('jpg', {}).get('image_url')
            rating = item.get('score') or 0
            year = item.get('published', {}).get('from', '')
            year = int(year.split('-')[0]) if year else 2000
            genres = [g['name'] for g in item.get('genres', [])]
            if not title:
                continue
            content, created = BaseContent.objects.update_or_create(
                title=title,
                content_type='manga',
                defaults={
                    'description': description,
                    'poster_url': poster or '',
                    'rating': rating,
                    'release_year': year
                }
            )
            content.genres.clear()
            for genre_name in genres:
                genre_obj, _ = Genre.objects.get_or_create(name=genre_name)
                content.genres.add(genre_obj)
        self.stdout.write(self.style.SUCCESS("✅ Manga imported successfully from Jikan API."))