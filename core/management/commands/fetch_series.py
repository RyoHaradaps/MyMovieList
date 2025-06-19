from django.core.management.base import BaseCommand
from core.models import BaseContent, Character, Staff
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
            tmdb_id = item.get('id')

            if not title or not first_air_date or not tmdb_id:
                continue

            year = int(first_air_date.split('-')[0])

            content, _ = BaseContent.objects.update_or_create(
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

            # Fetch cast and crew
            credits_url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/credits?api_key={API_KEY}"
            credits_response = requests.get(credits_url)
            if credits_response.status_code == 200:
                credits = credits_response.json()
                for cast in credits.get('cast', [])[:10]:
                    Character.objects.update_or_create(
                        name=cast['name'],
                        content=content,
                        defaults={'image_url': f"https://image.tmdb.org/t/p/w500{cast['profile_path']}" if cast.get('profile_path') else '', 'role': 'main'}
                    )
                for crew in credits.get('crew', []):
                    Staff.objects.update_or_create(
                        name=crew['name'],
                        role=crew['job'],
                        content=content,
                        defaults={'image_url': f"https://image.tmdb.org/t/p/w500{crew['profile_path']}" if crew.get('profile_path') else ''}
                    )

        self.stdout.write(self.style.SUCCESS("✅ Series imported successfully."))