from django.core.management.base import BaseCommand
from core.models import BaseContent, Genre
import requests
from django.conf import settings

class Command(BaseCommand):
    help = "Fetch and import Movies, Series, or AnimatedShows from TMDb API"

    def add_arguments(self, parser):
        parser.add_argument('content_type', choices=['movie', 'series', 'animatedshow'], help='Type of content to fetch')
        parser.add_argument('--pages', type=int, default=1, help='Number of pages to fetch (default: 1)')

    def handle(self, *args, **options):
        content_type = options['content_type']
        pages = options['pages']
        api_key = getattr(settings, 'TMDB_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR("TMDB_API_KEY not set in settings."))
            return

        if content_type == 'movie':
            endpoint = 'movie/popular'
        else:
            endpoint = 'tv/popular'

        for page in range(1, pages + 1):
            url = f'https://api.themoviedb.org/3/{endpoint}?api_key={api_key}&language=en-US&page={page}'
            resp = requests.get(url)
            if resp.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch data from TMDb (status {resp.status_code})"))
                continue
            results = resp.json().get('results', [])
            for item in results:
                tmdb_id = item['id']
                title = item.get('title') or item.get('name')
                overview = item.get('overview', '')
                poster_url = f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else ''
                release_year = (
                    int(item.get('release_date', '0000')[:4]) if item.get('release_date')
                    else int(item.get('first_air_date', '0000')[:4]) if item.get('first_air_date')
                    else 0
                )
                rating = item.get('vote_average', 0)

                # Determine content_type for animated shows
                if content_type == 'animatedshow':
                    # Only import if genre_ids contains 16 (Animation)
                    if 16 not in item.get('genre_ids', []):
                        continue

                # Save genres (optional, you can expand this)
                genres = item.get('genre_ids', [])
                genre_objs = []
                for gid in genres:
                    genre_name = str(gid)  # You can map TMDb genre IDs to names if you want
                    genre_obj, _ = Genre.objects.get_or_create(name=genre_name)
                    genre_objs.append(genre_obj)

                obj, created = BaseContent.objects.update_or_create(
                    tmdb_id=tmdb_id,
                    content_type=content_type,
                    defaults={
                        'title': title,
                        'description': overview,
                        'poster_url': poster_url,
                        'release_year': release_year,
                        'rating': rating,
                    }
                )
                if created:
                    obj.genres.set(genre_objs)
                self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'}: {title} (TMDb ID: {tmdb_id})"))

        self.stdout.write(self.style.SUCCESS(f"✅ {content_type.title()} import complete!"))
