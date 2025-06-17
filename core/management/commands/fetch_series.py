from django.core.management.base import BaseCommand
from core.models import BaseContent
import requests
from django.conf import settings

class Command(BaseCommand):
    help = "Fetch and import popular TV series from TMDb API"

    def handle(self, *args, **kwargs):
        API_KEY = getattr(settings, 'TMDB_API_KEY', None)
        if not API_KEY:
            self.stdout.write(self.style.ERROR("TMDB_API_KEY not set in settings."))
            return

        url = f"https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}&language=en-US&page=1"
        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Failed to fetch data from TMDb."))
            return

        data = response.json()

        for item in data.get('results', []):
            title = item.get('name')
            description = item.get('overview')
            poster = item.get('poster_path')
            rating = item.get('vote_average')
            first_air_date = item.get('first_air_date', '')

            if not title or not first_air_date:
                continue

            year = int(first_air_date.split('-')[0])

            BaseContent.objects.update_or_create(
                title=title,
                content_type='series',
                defaults={
                    'description': description,
                    'poster_url': f"https://image.tmdb.org/t/p/w500{poster}" if poster else '',
                    'genre': 'Unknown',
                    'rating': rating,
                    'release_year': year
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Series imported successfully."))