from django.core.management.base import BaseCommand
from core.models import BaseContent
import requests
from django.conf import settings

class Command(BaseCommand):
    help = "Fetch and import popular animated shows (cartoons) from TMDb API"

    def handle(self, *args, **kwargs):
        API_KEY = getattr(settings, 'TMDB_API_KEY', None)
        if not API_KEY:
            self.stdout.write(self.style.ERROR("TMDB_API_KEY not set in settings."))
            return

        # TMDb: Use the 'tv' endpoint and filter by genre for Animation (genre id 16)
        url = f"https://api.themoviedb.org/3/discover/tv?api_key={API_KEY}&with_genres=16&language=en-US&page=1"
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
                content_type='animatedshow',
                defaults={
                    'description': description,
                    'poster_url': f"https://image.tmdb.org/t/p/w500{poster}" if poster else '',
                    'genre': 'Animation',
                    'rating': rating,
                    'release_year': year
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Animated shows (cartoons) imported successfully."))