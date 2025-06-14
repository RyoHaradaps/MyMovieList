from django.core.management.base import BaseCommand
from core.models import BaseContent
import requests

class Command(BaseCommand):
    help = "Fetch and import popular movies from TMDb API"

    def handle(self, *args, **kwargs):
        API_KEY = '172374e15829559e06d62d17c7743aa4'  # 🔁 Replace this
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1"
        response = requests.get(url)
        data = response.json()

        for item in data.get('results', []):
            title = item.get('title')
            description = item.get('overview')
            poster = item.get('poster_path')
            rating = item.get('vote_average')
            release_date = item.get('release_date', '')

            if not title or not release_date:
                continue

            year = int(release_date.split('-')[0])

            BaseContent.objects.update_or_create(
                title=title,
                content_type='movie',
                defaults={
                    'description': description,
                    'poster_url': f"https://image.tmdb.org/t/p/w500{poster}" if poster else '',
                    'genre': 'Unknown',
                    'rating': rating,
                    'release_year': year
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Movies imported successfully."))
