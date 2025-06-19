from django.core.management.base import BaseCommand
from core.models import BaseContent, Character, VoiceActor, Staff, Theme
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
            mal_id = item.get('mal_id')

            if not title or not mal_id:
                continue

            content, _ = BaseContent.objects.update_or_create(
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

            # Fetch characters & voice actors
            characters_url = f"https://api.jikan.moe/v4/anime/{mal_id}/characters"
            char_response = requests.get(characters_url)
            if char_response.status_code == 200:
                for char in char_response.json().get('data', []):
                    character_obj, _ = Character.objects.update_or_create(
                        name=char['character']['name'],
                        content=content,
                        defaults={'image_url': char['character']['images']['jpg']['image_url'], 'role': char['role']}
                    )
                    for va in char.get('voice_actors', []):
                        va_obj, _ = VoiceActor.objects.update_or_create(
                            name=va['person']['name'],
                            defaults={'language': va['language'], 'image_url': va['person']['images']['jpg']['image_url']}
                        )
                        character_obj.voice_actors.add(va_obj)

            # Fetch staff
            staff_url = f"https://api.jikan.moe/v4/anime/{mal_id}/staff"
            staff_response = requests.get(staff_url)
            if staff_response.status_code == 200:
                for staff in staff_response.json().get('data', []):
                    Staff.objects.update_or_create(
                        name=staff['person']['name'],
                        role=staff['positions'][0] if staff['positions'] else '',
                        content=content,
                        defaults={'image_url': staff['person']['images']['jpg']['image_url']}
                    )

            # Fetch themes
            themes_url = f"https://api.jikan.moe/v4/anime/{mal_id}/themes"
            themes_response = requests.get(themes_url)
            if themes_response.status_code == 200:
                for op in themes_response.json().get('data', {}).get('openings', []):
                    Theme.objects.update_or_create(
                        content=content, type='opening', title=op, defaults={'artist': ''}
                    )
                for ed in themes_response.json().get('data', {}).get('endings', []):
                    Theme.objects.update_or_create(
                        content=content, type='ending', title=ed, defaults={'artist': ''}
                    )

        self.stdout.write(self.style.SUCCESS("✅ Anime imported successfully from Jikan API."))