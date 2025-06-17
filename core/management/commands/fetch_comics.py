from django.core.management.base import BaseCommand
from core.models import BaseContent
import requests
from django.conf import settings

class Command(BaseCommand):
    help = "Fetch and import comics from Comic Vine API"

    def handle(self, *args, **kwargs):
        API_KEY = getattr(settings, 'COMICVINE_API_KEY', None)
        if not API_KEY:
            self.stdout.write(self.style.ERROR("COMICVINE_API_KEY not set in settings."))
            return

        url = f"https://comicvine.gamespot.com/api/issues/?api_key={API_KEY}&format=json&sort=cover_date:desc&limit=20"
        headers = {'User-Agent': 'MyMovieList/1.0'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to fetch data from Comic Vine API."))
            return

        data = response.json()

        for item in data.get('results', []):
            title = item.get('name') or item.get('volume', {}).get('name')
            description = item.get('description') or item.get('synopsis') or "No description available."
            poster = item.get('image', {}).get('original_url')
            year = item.get('cover_date', '')
            year = int(year.split('-')[0]) if year else 2000
            rating = item.get('score') or 0

            if not title:
                continue

            BaseContent.objects.update_or_create(
                title=title,
                content_type='comic',
                defaults={
                    'description': description,
                    'poster_url': poster or '',
                    'genre': 'Comic',
                    'rating': rating,
                    'release_year': year
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Comics imported successfully from Comic Vine API."))