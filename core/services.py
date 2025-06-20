import requests
from django.conf import settings
from datetime import datetime, timedelta

def get_latest_animated_movies(target_count=12):
    api_key = settings.TMDB_API_KEY
    today_str = datetime.now().strftime('%Y-%m-%d')
    now_playing_url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={api_key}&language=en-US&page=1"
    
    latest_animated = []
    seen_ids = set()

    try:
        # First, try to get "Now Playing" animated movies
        response = requests.get(now_playing_url)
        response.raise_for_status()
        now_playing_movies = response.json().get('results', [])
        
        animated_now_playing = [
            movie for movie in now_playing_movies 
            if 16 in movie.get('genre_ids', [])
        ]
        
        for movie in animated_now_playing:
            if movie['id'] not in seen_ids:
                latest_animated.append(movie)
                seen_ids.add(movie['id'])

        # If we don't have enough, supplement with recent releases, ensuring they are not from the future
        if len(latest_animated) < target_count:
            discover_url = (
                f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}"
                f"&language=en-US&sort_by=primary_release_date.desc&with_genres=16"
                f"&primary_release_date.lte={today_str}"
            )
            page = 1
            while len(latest_animated) < target_count:
                discover_response = requests.get(f"{discover_url}&page={page}")
                discover_response.raise_for_status()
                data = discover_response.json()
                recent_movies = data.get('results', [])

                if not recent_movies:
                    break 

                for movie in recent_movies:
                    if movie['id'] not in seen_ids:
                        latest_animated.append(movie)
                        seen_ids.add(movie['id'])
                        if len(latest_animated) >= target_count:
                            break
                
                page += 1
                if page > data.get('total_pages', page):
                    break

        return latest_animated[:target_count]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest animated movies: {e}")
        return []

def get_upcoming_animated_movies(target_count=12):
    api_key = settings.TMDB_API_KEY
    # Use tomorrow's date to be certain we only get future releases
    tomorrow = datetime.now().date() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')

    # Use the 'discover' endpoint for more reliable date filtering
    discover_url = (
        f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}"
        f"&language=en-US&sort_by=primary_release_date.asc&with_genres=16"
        f"&primary_release_date.gte={tomorrow_str}"
    )
    
    upcoming_animated = []
    seen_ids = set()
    page = 1

    try:
        # Paginate until we have enough movies or run out of pages
        while len(upcoming_animated) < target_count and page <= 5: # Limit to 5 pages
            response = requests.get(f"{discover_url}&page={page}")
            response.raise_for_status()
            data = response.json()
            
            upcoming_movies = data.get('results', [])
            if not upcoming_movies:
                break

            for movie in upcoming_movies:
                if len(upcoming_animated) >= target_count:
                    break
                # Perform a manual date check as a safeguard
                release_date_str = movie.get('release_date')
                if movie['id'] not in seen_ids and release_date_str:
                    try:
                        release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                        if release_date >= tomorrow:
                            upcoming_animated.append(movie)
                            seen_ids.add(movie['id'])
                    except ValueError:
                        continue # Skip movies with invalid date formats
            
            page += 1
            if page > data.get('total_pages', page):
                break

        return upcoming_animated[:target_count]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching upcoming animated movies: {e}")
        return [] 