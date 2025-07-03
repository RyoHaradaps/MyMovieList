from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import BaseContent, Profile, Watchlist, ContentRelation, Genre
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone
import requests
from django.conf import settings
from .services import get_latest_animated_movies, get_upcoming_animated_movies
from django.http import Http404
from collections import defaultdict
from django.views.decorators.http import require_POST
from django.urls import reverse

# Create your views here.
def index(request):
    # If user is logged in, redirect to home page
    if 'profile_id' in request.session:
        try:
            # Verify the profile exists to avoid session errors
            Profile.objects.get(id=request.session['profile_id'])
            return redirect('home')
        except Profile.DoesNotExist:
            # If profile in session is invalid, clear it and show index
            del request.session['profile_id']

    # Public landing page: show popular content for everyone
    trending = BaseContent.objects.filter(content_type='movie').order_by('-rating')[:12]
    top_series = BaseContent.objects.filter(content_type='series').order_by('-rating')[:12]
    top_animated = BaseContent.objects.filter(content_type='animatedshow').order_by('-rating')[:12]
    top_comics = BaseContent.objects.filter(content_type='comic').order_by('-rating')[:12]
    
    return render(request, 'core/index.html', {
        'trending': trending,
        'top_series': top_series,
        'top_animated': top_animated,
        'top_comics': top_comics,
        'profile': None,
    })

def register_view(request):
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        month = request.POST.get('month')
        day = request.POST.get('day')
        year = request.POST.get('year')

        # Combine birthday fields
        try:
            birthday_str = f"{year}-{month}-{day}"
            birthday = datetime.strptime(birthday_str, "%Y-%B-%d").date()
        except Exception:
            messages.error(request, "Invalid birthday")
            return redirect('register')

        if Profile.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('register')
        if Profile.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        # WARNING: Passwords should be hashed! This is plain text for demo only.
        Profile.objects.create(
            username=username,
            email=email,
            password=make_password(password),  # Hash the password!
            birthday=birthday
        )
        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'core/register.html', {'months': months, 'hide_navbar': True})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            profile = Profile.objects.get(username=username)
            if check_password(password, profile.password):
                request.session['profile_id'] = profile.id
                messages.success(request, "Logged in successfully")
                return redirect('index')  # <--- Redirect to index page
            else:
                messages.error(request, "Invalid credentials")
        except Profile.DoesNotExist:
            messages.error(request, "Invalid credentials")

        return redirect('login')
    return render(request, 'core/login.html', {'hide_navbar': True})

def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')

def home_view(request):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('index')

    try:
        profile = Profile.objects.get(id=profile_id)
        if not profile:
            # If profile_id in session is invalid, clear it and redirect to index
            if 'profile_id' in request.session:
                del request.session['profile_id']
            return redirect('index')
    except Profile.DoesNotExist:
        # If profile_id in session is invalid, clear it and redirect to index
        if 'profile_id' in request.session:
            del request.session['profile_id']
        return redirect('index')

    continue_watching = []
    recent_watchlist = []
    
    watchlist_items = Watchlist.objects.filter(profile=profile).select_related('content')
    # "Continue Watching" carousel
    continue_watching = [item.content for item in watchlist_items.filter(status='watching').order_by('-added_on')[:12]]
    # "Recently Added to Watchlist" carousel
    recent_watchlist = [item.content for item in watchlist_items.order_by('-added_on')[:12]]

    # Popular Carousels for all content types
    popular_carousels = []
    TMDB_API_KEY = getattr(settings, 'TMDB_API_KEY', None)
    COMICVINE_API_KEY = getattr(settings, 'COMICVINE_API_KEY', None)

    try:
        # Popular Movies
        if TMDB_API_KEY:
            movies_url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}'
            movies_resp = requests.get(movies_url).json().get('results', [])
            popular_carousels.append({
                'title': 'Popular Movies',
                'content': [{'pk': m.get('id'), 'title': m.get('title'), 'poster_url': f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}", 'release_year': m.get('release_date', '')[:4], 'rating': m.get('vote_average')} for m in movies_resp[:12]]
            })

        # Popular Series (excluding talk shows)
        if TMDB_API_KEY:
            series_url = f'https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&sort_by=popularity.desc&without_genres=10767,10763'
            series_resp = requests.get(series_url).json().get('results', [])
            popular_carousels.append({
                'title': 'Popular Series',
                'content': [{'pk': s.get('id'), 'title': s.get('name'), 'poster_url': f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}", 'release_year': s.get('first_air_date', '')[:4], 'rating': s.get('vote_average')} for s in series_resp[:12]]
            })

        # Popular Anime
        anime_url = 'https://api.jikan.moe/v4/top/anime?filter=bypopularity'
        anime_resp = requests.get(anime_url).json().get('data', [])
        popular_carousels.append({
            'title': 'Popular Anime',
            'content': [{'pk': a.get('mal_id'), 'title': a.get('title'), 'poster_url': a.get('images', {}).get('jpg', {}).get('large_image_url'), 'release_year': a.get('year'), 'rating': a.get('score')} for a in anime_resp[:12]]
        })

        # Popular Animated Shows
        if TMDB_API_KEY:
            animated_url = f'https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&with_genres=16&sort_by=popularity.desc'
            animated_resp = requests.get(animated_url).json().get('results', [])
            popular_carousels.append({
                'title': 'Popular Animated Shows',
                'content': [{'pk': s.get('id'), 'title': s.get('name'), 'poster_url': f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}", 'release_year': s.get('first_air_date', '')[:4], 'rating': s.get('vote_average')} for s in animated_resp if 'JP' not in s.get('origin_country', [])][:12]
            })

        # Popular Manga
        manga_url = 'https://api.jikan.moe/v4/top/manga?filter=bypopularity'
        manga_resp = requests.get(manga_url).json().get('data', [])
        popular_carousels.append({
            'title': 'Popular Manga',
            'content': [{'pk': m.get('mal_id'), 'title': m.get('title'), 'poster_url': m.get('images', {}).get('jpg', {}).get('large_image_url'), 'release_year': m.get('published', {}).get('from', '')[:4], 'rating': m.get('score')} for m in manga_resp[:12]]
        })

        # Popular Comics
        if COMICVINE_API_KEY:
            comics_url = f'https://comicvine.gamespot.com/api/issues/?api_key={COMICVINE_API_KEY}&format=json&sort=popularity:desc'
            comics_resp = requests.get(comics_url, headers={'User-Agent': 'MyMovieList/1.0'}).json().get('results', [])
            popular_carousels.append({
                'title': 'Popular Comics',
                'content': [{'pk': c.get('id'), 'title': c.get('name') or c.get('volume', {}).get('name', ''), 'poster_url': c.get('image', {}).get('original_url', ''), 'release_year': c.get('cover_date', '')[:4], 'rating': None} for c in comics_resp[:12]]
            })

    except Exception:
        # In case of API errors, the carousels list will be empty and nothing will be shown.
        pass

    context = {
        'profile': profile,
        'continue_watching': continue_watching,
        'recent_watchlist': recent_watchlist,
        'recommended_carousels': popular_carousels,
    }
    return render(request, 'core/home.html', context)

def search(request):
    # Dummy implementation, just renders the index page for now
    return render(request, 'core/index.html', {'movies': []})

def profile(request, username):
    profile = get_object_or_404(Profile, username=username)
    watchlist = Watchlist.objects.filter(profile=profile)

    # Content types
    content_types = ['movie', 'series', 'animatedshow']

    # Stats for content (anime/movies/series)
    stats_qs = watchlist.filter(content__content_type__in=content_types)
    stats = {
        'watching': stats_qs.filter(status='watching').count(),
        'completed': stats_qs.filter(status='completed').count(),
        'on_hold': stats_qs.filter(status='on_hold').count(),
        'dropped': stats_qs.filter(status='dropped').count(),
        'plan_to_watch': stats_qs.filter(status='plan_to_watch').count(),
        'total': stats_qs.count(),
        'mean_score': round(stats_qs.filter(score__isnull=False).aggregate(models.Avg('score'))['score__avg'] or 0, 2),
        'rewatched': stats_qs.aggregate(models.Sum('rewatched'))['rewatched__sum'] or 0,
        'episodes': stats_qs.aggregate(models.Sum('progress'))['progress__sum'] or 0,
    }
    stats['completed_percent'] = int((stats['completed'] / stats['total']) * 100) if stats['total'] else 0
    stats['days'] = round((stats['episodes'] / 24), 1) if stats['episodes'] else 0  # assuming 1 episode = 1 hour

    # Stats for comics
    comic_qs = watchlist.filter(content__content_type='comic')
    comic_stats = {
        'reading': comic_qs.filter(status='watching').count(),
        'completed': comic_qs.filter(status='completed').count(),
        'on_hold': comic_qs.filter(status='on_hold').count(),
        'dropped': comic_qs.filter(status='dropped').count(),
        'plan_to_read': comic_qs.filter(status='plan_to_read').count(),
        'total': comic_qs.count(),
        'mean_score': round(comic_qs.filter(score__isnull=False).aggregate(models.Avg('score'))['score__avg'] or 0, 2),
        'reread': comic_qs.aggregate(models.Sum('reread'))['reread__sum'] or 0,
        'chapters': comic_qs.aggregate(models.Sum('progress'))['progress__sum'] or 0,
    }
    comic_stats['completed_percent'] = int((comic_stats['completed'] / comic_stats['total']) * 100) if comic_stats['total'] else 0
    comic_stats['days'] = round((comic_stats['chapters'] / 24), 1) if comic_stats['chapters'] else 0  # assuming 1 chapter = 1 hour

    # Last content updates (not comics)
    last_content_updates = stats_qs.order_by('-added_on')[:3]

    # Last comic updates
    last_comic_updates = comic_qs.order_by('-added_on')[:5]

    total = stats['total'] or 1  # avoid division by zero
    percentages = {
        'watching': int((stats['watching'] / total) * 100),
        'completed': int((stats['completed'] / total) * 100),
        'on_hold': int((stats['on_hold'] / total) * 100),
        'dropped': int((stats['dropped'] / total) * 100),
        'plan_to_watch': int((stats['plan_to_watch'] / total) * 100),
    }

    context = {
        'profile': profile,
        'watchlist': watchlist,
        'stats': stats,
        'comic_stats': comic_stats,
        'last_content_updates': last_content_updates,
        'last_comic_updates': last_comic_updates,
        'percentages': percentages,
    }
    return render(request, 'core/profile.html', context)

def profile_edit(request):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        messages.error(request, "You must be logged in to edit your profile.")
        return redirect('login')
    profile = Profile.objects.get(id=profile_id)

    if request.method == 'POST':
        if request.POST.get('remove_avatar'):
            if profile.avatar:
                profile.avatar.delete(save=False)
                profile.avatar = None
                profile.save()
                messages.success(request, "Avatar removed successfully!")
            return redirect('profile_edit')
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        profile.bio = request.POST.get('bio', '')
        profile.gender = request.POST.get('gender', '')
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile', username=profile.username)

    return render(request, 'core/profile_edit.html', {'profile': profile})

def movie_list(request):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('login')
    
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    # Get status filter from GET params
    status = request.GET.get('status')
    watchlist_items = Watchlist.objects.filter(
        profile=profile,
        content__content_type='movie'
    ).select_related('content').order_by('-added_on')

    if status and status != 'all':
        watchlist_items = watchlist_items.filter(status=status)

    return render(request, 'core/list_page.html', {
        'items': watchlist_items,
        'type': 'Movie',
        'profile': profile,
        'is_watchlist': True,
        'current_status': status or 'all',
    })

def series_list(request):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('login')
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('login')
    # Only series WITHOUT Animation genre
    watchlist_items = Watchlist.objects.filter(
        profile=profile,
        content__content_type='series'
    ).exclude(content__genres__name='Animation').select_related('content').order_by('-added_on').distinct()

    return render(request, 'core/list_page.html', {
        'items': [item.content for item in watchlist_items],
        'type': 'Series',
        'profile': profile,
        'is_watchlist': True,
    })

def animated_list(request):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('login')
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('login')
    # Only series with Animation genre
    watchlist_items = Watchlist.objects.filter(
        profile=profile,
        content__content_type='series',
        content__genres__name='Animation'
    ).select_related('content').order_by('-added_on').distinct()

    return render(request, 'core/list_page.html', {
        'items': [item.content for item in watchlist_items],
        'type': 'Animated',
        'profile': profile,
        'is_watchlist': True,
    })

def anime_list(request):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('login')
    
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    # Get user's watchlist for anime only
    watchlist_items = Watchlist.objects.filter(
        profile=profile,
        content__content_type='anime'
    ).select_related('content').order_by('-added_on')
    
    return render(request, 'core/list_page.html', {
        'items': [item.content for item in watchlist_items],
        'type': 'Anime',
        'profile': profile,
        'is_watchlist': True,
    })

def manga_list(request):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('login')
    
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    # Get user's watchlist for manga only
    watchlist_items = Watchlist.objects.filter(
        profile=profile,
        content__content_type='manga'
    ).select_related('content').order_by('-added_on')
    
    return render(request, 'core/list_page.html', {
        'items': [item.content for item in watchlist_items],
        'type': 'Manga',
        'profile': profile,
        'is_watchlist': True,
    })

def comic_list(request):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('login')
    
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    # Get user's watchlist for comics only
    watchlist_items = Watchlist.objects.filter(
        profile=profile,
        content__content_type='comic'
    ).select_related('content').order_by('-added_on')
    
    return render(request, 'core/list_page.html', {
        'items': [item.content for item in watchlist_items],
        'type': 'Comic',
        'profile': profile,
        'is_watchlist': True,
    })

def content_detail(request, pk):
    content = get_object_or_404(BaseContent, pk=pk)
    tmdb_data = None
    runtime = None
    videos = []
    seasons = []
    cast = []
    crew = []
    grouped_staff = []
    if content.content_type in ['movie', 'series', 'animatedshow'] and content.tmdb_id:
        tmdb_type = 'movie' if content.content_type == 'movie' else 'tv'
        api_key = settings.TMDB_API_KEY
        url = f'https://api.themoviedb.org/3/{tmdb_type}/{content.tmdb_id}?api_key={api_key}&language=en-US'
        resp = requests.get(url)
        if resp.status_code == 200:
            tmdb_data = resp.json()
            if 'runtime' in tmdb_data and tmdb_data['runtime']:
                minutes = tmdb_data['runtime']
                hours = minutes // 60
                minutes = minutes % 60
                runtime = f"{hours}h {minutes}m" if hours else f"{minutes}m"
            # Fetch extra TMDB data for series/animatedshow
            if tmdb_type == 'tv':
                # Credits
                credits_url = f'https://api.themoviedb.org/3/tv/{content.tmdb_id}/credits?api_key={api_key}'
                credits_resp = requests.get(credits_url)
                credits = credits_resp.json() if credits_resp.status_code == 200 else {}
                cast = credits.get('cast', [])
                crew = credits.get('crew', [])
                grouped_staff = group_staff_by_person(crew)
                # Videos
                videos_url = f'https://api.themoviedb.org/3/tv/{content.tmdb_id}/videos?api_key={api_key}'
                videos_resp = requests.get(videos_url)
                videos = videos_resp.json().get('results', []) if videos_resp.status_code == 200 else []
                # Seasons/Episodes
                seasons = fetch_tmdb_seasons_and_episodes(content.tmdb_id)
            elif tmdb_type == 'movie':
                # Credits
                credits_url = f'https://api.themoviedb.org/3/movie/{content.tmdb_id}/credits?api_key={api_key}'
                credits_resp = requests.get(credits_url)
                credits = credits_resp.json() if credits_resp.status_code == 200 else {}
                cast = credits.get('cast', [])
                crew = credits.get('crew', [])
                grouped_staff = group_staff_by_person(crew)
                # Videos
                videos_url = f'https://api.themoviedb.org/3/movie/{content.tmdb_id}/videos?api_key={api_key}'
                videos_resp = requests.get(videos_url)
                videos = videos_resp.json().get('results', []) if videos_resp.status_code == 200 else []
                # Movies don't have seasons
    else:
        # fallback to local DB data for characters/staff
        cast = content.characters.all().prefetch_related('voice_actors')
        grouped_staff = content.staff.all()

    related_entries = ContentRelation.objects.filter(from_content=content).select_related('to_content')
    themes = content.themes.all()

    # Fetch user's Watchlist entry if logged in
    watchlist_entry = None
    profile_id = request.session.get('profile_id')
    if profile_id:
        try:
            profile = Profile.objects.get(pk=profile_id)
            watchlist_entry = Watchlist.objects.filter(profile=profile, content=content).first()
        except Profile.DoesNotExist:
            pass

    status_choices = Watchlist._meta.get_field('status').choices
    score_labels = [
        (10, "Masterpiece"), (9, "Great"), (8, "Very Good"), (7, "Good"), (6, "Fine"),
        (5, "Average"), (4, "Bad"), (3, "Very Bad"), (2, "Horrible"), (1, "Appalling"),
    ]

    print("DEBUG: content =", content)
    print("DEBUG: tmdb_data =", tmdb_data)

    return render(request, 'core/content_detail.html', {
        'content': content,
        'tmdb_data': tmdb_data,
        'related_entries': related_entries,
        'characters': cast,
        'staff': grouped_staff,
        'themes': themes,
        'videos': videos,
        'seasons': seasons,
        'watchlist_entry': watchlist_entry,
        'status_choices': status_choices,
        'score_labels': score_labels,
    })

def movies_showcase(request):
    TMDB_API_KEY = getattr(settings, 'TMDB_API_KEY', None)
    trending, popular, latest, coming_soon = [], [], [], []
    if TMDB_API_KEY:
        try:
            # Trending (Now Playing in theaters)
            trending_url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}'
            trending_resp = requests.get(trending_url)
            trending = [
                {
                    'title': m.get('title'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get('poster_path') else '',
                    'release_year': m.get('release_date', '')[:4],
                    'rating': m.get('vote_average'),
                    'pk': m.get('id'),
                } for m in trending_resp.json().get('results', [])[:12]
            ]
            # Popular
            popular_url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}'
            popular_resp = requests.get(popular_url)
            popular = [
                {
                    'title': m.get('title'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get('poster_path') else '',
                    'release_year': m.get('release_date', '')[:4],
                    'rating': m.get('vote_average'),
                    'pk': m.get('id'),
                } for m in popular_resp.json().get('results', [])[:12]
            ]
            # Latest (recently released movies)
            latest_url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}'
            latest_resp = requests.get(latest_url)
            latest = [
                {
                    'title': m.get('title'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get('poster_path') else '',
                    'release_year': m.get('release_date', '')[:4],
                    'rating': m.get('vote_average'),
                    'pk': m.get('id'),
                } for m in latest_resp.json().get('results', [])[:12]
            ]
            # Coming Soon (upcoming movies)
            coming_soon_url = f'https://api.themoviedb.org/3/movie/upcoming?api_key={TMDB_API_KEY}'
            coming_soon_resp = requests.get(coming_soon_url)
            coming_soon = [
                {
                    'title': m.get('title'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get('poster_path') else '',
                    'release_year': m.get('release_date', '')[:4],
                    'rating': m.get('vote_average'),
                    'pk': m.get('id'),
                } for m in coming_soon_resp.json().get('results', [])[:12]
            ]
        except Exception:
            trending, popular, latest, coming_soon = [], [], [], []
    return render(request, 'core/content_showcase.html', {
        'type': 'movie',
        'trending': trending,
        'popular': popular,
        'latest': latest,
        'coming_soon': coming_soon,
    })

def series_showcase(request):
    TMDB_API_KEY = getattr(settings, 'TMDB_API_KEY', None)
    trending, popular, latest, coming_soon = [], [], [], []
    if TMDB_API_KEY:
        try:
            # Trending TV - Use dedicated trending endpoint and exclude animated/talk shows
            trending_url = f'https://api.themoviedb.org/3/trending/tv/week?api_key={TMDB_API_KEY}'
            trending_resp = requests.get(trending_url)
            trending = [
                {
                    'title': s.get('name'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get('poster_path') else '',
                    'release_year': s.get('first_air_date', '')[:4],
                    'rating': s.get('vote_average'),
                    'pk': s.get('id'),
                } for s in trending_resp.json().get('results', [])
                if 16 not in s.get('genre_ids', []) and 10767 not in s.get('genre_ids', [])
            ][:12]
            
            # Popular TV - Exclude animated content (16) and talk shows (10767)
            popular_url = f'https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&sort_by=popularity.desc&without_genres=16,10767'
            popular_resp = requests.get(popular_url)
            popular = [
                {
                    'title': s.get('name'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get('poster_path') else '',
                    'release_year': s.get('first_air_date', '')[:4],
                    'rating': s.get('vote_average'),
                    'pk': s.get('id'),
                } for s in popular_resp.json().get('results', []) 
                if 'JP' not in s.get('origin_country', [])  # Exclude Japanese content
            ][:12]
            
            # Latest TV (airing today or already aired) - Exclude animated and talk shows
            today = datetime.now().strftime('%Y-%m-%d')
            latest_url = f'https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&sort_by=first_air_date.desc&without_genres=16,10767&first_air_date.lte={today}'
            latest_resp = requests.get(latest_url)
            latest = [
                {
                    'title': s.get('name'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get('poster_path') else '',
                    'release_year': s.get('first_air_date', '')[:4],
                    'rating': s.get('vote_average'),
                    'pk': s.get('id'),
                } for s in latest_resp.json().get('results', []) 
                if 'JP' not in s.get('origin_country', [])  # Exclude Japanese content
            ][:12]
            
            # Coming Soon TV (upcoming, not yet aired) - Exclude animated and talk shows
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            coming_soon_url = (
                f'https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}'
                f'&language=en-US&sort_by=popularity.desc'
                f'&first_air_date.gte={tomorrow}&first_air_date.lte={future_date}'
                f'&without_genres=16,10767'  # Exclude animated and talk shows
                f'&with_type=2|3|4|5'  # Excludes some unwanted types
            )
            coming_soon_resp = requests.get(coming_soon_url)
            coming_soon = [
                {
                    'title': s.get('name'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get('poster_path') else '',
                    'release_year': s.get('first_air_date', '')[:4],
                    'rating': s.get('vote_average'),
                    'pk': s.get('id'),
                } for s in coming_soon_resp.json().get('results', []) 
                if 'JP' not in s.get('origin_country', [])  # Exclude Japanese content
            ][:12]
        except Exception:
            trending, popular, latest, coming_soon = [], [], [], []
    return render(request, 'core/content_showcase.html', {
        'type': 'series',
        'trending': trending,
        'popular': popular,
        'latest': latest,
        'coming_soon': coming_soon,
    })

def anime_showcase(request):
    trending, popular, latest, coming_soon = [], [], [], []
    try:
        # Trending: currently airing TV anime (current season)
        trending_url = 'https://api.jikan.moe/v4/seasons/now'
        trending_resp = requests.get(trending_url)
        trending = [
            {
                'title': a['title'],
                'poster_url': a['images']['jpg']['large_image_url'] if a.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                'release_year': a.get('year') or (a.get('aired', {}).get('from', '')[:4] if a.get('aired', {}).get('from') else ''),
                'rating': a.get('score'),
                'pk': a.get('mal_id'),
            }
            for a in trending_resp.json().get('data', []) if a.get('type') == 'TV'
        ][:12]

        # Popular: by popularity, TV anime only
        popular_url = 'https://api.jikan.moe/v4/top/anime?filter=bypopularity'
        popular_resp = requests.get(popular_url)
        popular = [
            {
                'title': a['title'],
                'poster_url': a['images']['jpg']['large_image_url'] if a.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                'release_year': a.get('year') or (a.get('aired', {}).get('from', '')[:4] if a.get('aired', {}).get('from') else ''),
                'rating': a.get('score'),
                'pk': a.get('mal_id'),
            }
            for a in popular_resp.json().get('data', []) if a.get('type') == 'TV'
        ][:12]

        # Latest: currently airing TV anime (real-time, fallback to current season if needed)
        latest = []
        # 1. Try currently airing
        airing_url = 'https://api.jikan.moe/v4/anime?status=airing&order_by=start_date&sort=desc&limit=20'
        airing_resp = requests.get(airing_url)
        airing_data = airing_resp.json().get('data', [])
        latest = [
            {
                'title': a['title'],
                'poster_url': a['images']['jpg']['large_image_url'] if a.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                'release_year': a.get('year') or (a.get('aired', {}).get('from', '')[:4] if a.get('aired', {}).get('from') else ''),
                'rating': a.get('score'),
                'pk': a.get('mal_id'),
            }
            for a in airing_data if a.get('type') == 'TV'
        ]
        # 2. Fallback: supplement with current season if not enough
        if len(latest) < 12:
            def get_current_season():
                month = datetime.now().month
                if month in [12, 1, 2]:
                    return 'winter'
                elif month in [3, 4, 5]:
                    return 'spring'
                elif month in [6, 7, 8]:
                    return 'summer'
                else:
                    return 'fall'
            year = datetime.now().year
            season = get_current_season()
            season_url = f'https://api.jikan.moe/v4/seasons/{year}/{season}'
            season_resp = requests.get(season_url)
            season_data = season_resp.json().get('data', [])
            # Filter out duplicates
            existing_ids = {a['pk'] for a in latest}
            for a in season_data:
                if a.get('type') == 'TV' and a.get('mal_id') not in existing_ids:
                    latest.append({
                        'title': a['title'],
                        'poster_url': a['images']['jpg']['large_image_url'] if a.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                        'release_year': a.get('year') or (a.get('aired', {}).get('from', '')[:4] if a.get('aired', {}).get('from') else ''),
                        'rating': a.get('score'),
                        'pk': a.get('mal_id'),
                    })
                if len(latest) >= 12:
                    break
        # Deduplicate latest by mal_id (pk)
        unique_latest = []
        seen_ids = set()
        for anime in latest:
            if anime['pk'] not in seen_ids:
                unique_latest.append(anime)
                seen_ids.add(anime['pk'])
        latest = unique_latest[:12]

        # Coming Soon: upcoming TV anime, EXCLUDING those already in 'latest', then deduplicate
        latest_ids = {a['pk'] for a in latest}
        coming_soon_url = 'https://api.jikan.moe/v4/seasons/upcoming'
        coming_soon_resp = requests.get(coming_soon_url)
        raw_coming_soon = [
            {
                'title': a['title'],
                'poster_url': a['images']['jpg']['large_image_url'] if a.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                'release_year': a.get('year') or (a.get('aired', {}).get('from', '')[:4] if a.get('aired', {}).get('from') else ''),
                'rating': a.get('score'),
                'pk': a.get('mal_id'),
            }
            for a in coming_soon_resp.json().get('data', [])
            if a.get('type') == 'TV' and a.get('mal_id') not in latest_ids
        ]
        # Deduplicate by mal_id
        unique_coming_soon = []
        seen_ids = set()
        for anime in raw_coming_soon:
            if anime['pk'] not in seen_ids:
                unique_coming_soon.append(anime)
                seen_ids.add(anime['pk'])
        coming_soon = unique_coming_soon[:12]
        # Fallback: if empty, show up to 12 unique upcoming TV anime (even if some overlap with latest)
        if not coming_soon:
            raw_coming_soon = [
                {
                    'title': a['title'],
                    'poster_url': a['images']['jpg']['large_image_url'] if a.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                    'release_year': a.get('year') or (a.get('aired', {}).get('from', '')[:4] if a.get('aired', {}).get('from') else ''),
                    'rating': a.get('score'),
                    'pk': a.get('mal_id'),
                }
                for a in coming_soon_resp.json().get('data', [])
                if a.get('type') == 'TV'
            ]
            unique_coming_soon = []
            seen_ids = set()
            for anime in raw_coming_soon:
                if anime['pk'] not in seen_ids:
                    unique_coming_soon.append(anime)
                    seen_ids.add(anime['pk'])
            coming_soon = unique_coming_soon[:12]

    except Exception:
        trending, popular, latest, coming_soon = [], [], [], []

    return render(request, 'core/content_showcase.html', {
        'type': 'anime',
        'trending': trending,
        'popular': popular,
        'latest': latest,
        'coming_soon': coming_soon,
    })

def animated_showcase(request):
    TMDB_API_KEY = getattr(settings, 'TMDB_API_KEY', None)
    trending, popular, latest, coming_soon = [], [], [], []
    if TMDB_API_KEY:
        try:
            # Trending: Most popular animated TV (Western only)
            trending_url = f'https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&with_genres=16&sort_by=popularity.desc'
            trending_resp = requests.get(trending_url)
            trending = [
                {
                    'title': s.get('name'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get('poster_path') else '',
                    'release_year': s.get('first_air_date', '')[:4],
                    'rating': s.get('vote_average'),
                    'pk': s.get('id'),
                }
                for s in trending_resp.json().get('results', []) if 'JP' not in s.get('origin_country', [])
            ][:12]

            # Popular: Most popular animated TV (Western only)
            popular_url = f'https://api.themoviedb.org/3/discover/tv?api_key={TMDB_API_KEY}&with_genres=16&sort_by=vote_average.desc&vote_count.gte=100'
            popular_resp = requests.get(popular_url)
            popular = [
                {
                    'title': s.get('name'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get('poster_path') else '',
                    'release_year': s.get('first_air_date', '')[:4],
                    'rating': s.get('vote_average'),
                    'pk': s.get('id'),
                }
                for s in popular_resp.json().get('results', []) if 'JP' not in s.get('origin_country', [])
            ][:12]

            # Latest: "Now Playing" and recent animated movies from TMDB
            latest_raw = get_latest_animated_movies()
            latest = [
                {
                    'title': m.get('title'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get('poster_path') else '',
                    'release_year': m.get('release_date', '')[:4],
                    'rating': m.get('vote_average'),
                    'pk': m.get('id'),
                } for m in latest_raw
            ]

            # Coming Soon: Upcoming animated movies from TMDB
            coming_soon_raw = get_upcoming_animated_movies()
            coming_soon = [
                {
                    'title': m.get('title'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get('poster_path') else '',
                    'release_year': m.get('release_date', '')[:4],
                    'rating': m.get('vote_average'),
                    'pk': m.get('id'),
                } for m in coming_soon_raw
            ]
        except Exception:
            trending, popular, latest, coming_soon = [], [], [], []
    return render(request, 'core/content_showcase.html', {
        'type': 'animated',
        'trending': trending,
        'popular': popular,
        'latest': latest,
        'coming_soon': coming_soon,
    })

def unique_issues_by_title(issues, max_items=12):
    seen = set()
    unique = []
    for issue in issues:
        title = issue.get('name') or issue.get('volume', {}).get('name', '')
        if title and title not in seen:
            seen.add(title)
            unique.append({
                'title': title,
                'poster_url': issue.get('image', {}).get('original_url', ''),
                'release_year': issue.get('cover_date', '')[:4],
                'rating': issue.get('site_detail_url'),
                'pk': issue.get('id'),
            })
        if len(unique) >= max_items:
            break
    return unique

def comics_showcase(request):
    COMICVINE_API_KEY = getattr(settings, 'COMICVINE_API_KEY', None)
    trending, popular, latest, coming_soon = [], [], [], []
    if COMICVINE_API_KEY:
        try:
            # Calculate date 30 days ago
            today = datetime.today()
            last_month = (today - timedelta(days=30)).strftime('%Y-%m-%d')
            today_str = today.strftime('%Y-%m-%d')

            # Trending: Most popular issues released in the last 30 days, unique titles only
            trending_url = (
                f'https://comicvine.gamespot.com/api/issues/?api_key={COMICVINE_API_KEY}'
                f'&format=json&filter=cover_date:{last_month}|{today_str}&sort=popularity:desc'
            )
            trending_resp = requests.get(trending_url, headers={'User-Agent': 'MyMovieList/1.0'})
            trending = unique_issues_by_title(trending_resp.json().get('results', []), max_items=12)

            # Popular: Most popular issues overall
            popular_url = f'https://comicvine.gamespot.com/api/issues/?api_key={COMICVINE_API_KEY}&format=json&sort=popularity:desc'
            popular_resp = requests.get(popular_url, headers={'User-Agent': 'MyMovieList/1.0'})
            popular = [
                {
                    'title': c.get('name') or c.get('volume', {}).get('name', ''),
                    'poster_url': c.get('image', {}).get('original_url', ''),
                    'release_year': c.get('cover_date', '')[:4],
                    'rating': c.get('site_detail_url'),
                    'pk': c.get('id'),
                } for c in popular_resp.json().get('results', [])[:12]
            ]

            # Latest: Most recently released issues
            latest_url = f'https://comicvine.gamespot.com/api/issues/?api_key={COMICVINE_API_KEY}&format=json&sort=cover_date:desc'
            latest_resp = requests.get(latest_url, headers={'User-Agent': 'MyMovieList/1.0'})
            latest = [
                {
                    'title': c.get('name') or c.get('volume', {}).get('name', ''),
                    'poster_url': c.get('image', {}).get('original_url', ''),
                    'release_year': c.get('cover_date', '')[:4],
                    'rating': c.get('site_detail_url'),
                    'pk': c.get('id'),
                } for c in latest_resp.json().get('results', [])[:12]
            ]

            # Coming Soon: (keep as before or hide if not useful)
            coming_soon = []

        except Exception:
            trending, popular, latest, coming_soon = [], [], [], []
    return render(request, 'core/content_showcase.html', {
        'type': 'comic',
        'trending': trending,
        'popular': popular,
        'latest': latest,
        'coming_soon': coming_soon,
    })

def manga_showcase(request):
    trending, popular, latest, coming_soon = [], [], [], []
    try:
        # Trending: currently publishing manga
        trending_url = 'https://api.jikan.moe/v4/top/manga?filter=publishing'
        trending_resp = requests.get(trending_url)
        trending = [
            {
                'title': m['title'],
                'poster_url': m['images']['jpg']['large_image_url'] if m.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                'release_year': m.get('published', {}).get('from', '')[:4] if m.get('published', {}).get('from') else '',
                'rating': m.get('score'),
                'pk': m.get('mal_id'),
            }
            for m in trending_resp.json().get('data', [])[:12]
        ]

        # What's Popular: by popularity
        popular_url = 'https://api.jikan.moe/v4/top/manga?filter=bypopularity'
        popular_resp = requests.get(popular_url)
        popular = [
            {
                'title': m['title'],
                'poster_url': m['images']['jpg']['large_image_url'] if m.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                'release_year': m.get('published', {}).get('from', '')[:4] if m.get('published', {}).get('from') else '',
                'rating': m.get('score'),
                'pk': m.get('mal_id'),
            }
            for m in popular_resp.json().get('data', [])[:12]
        ]

        # Latest: order by start_date descending
        latest_url = 'https://api.jikan.moe/v4/manga?order_by=start_date&sort=desc'
        latest_resp = requests.get(latest_url)
        latest = [
            {
                'title': m['title'],
                'poster_url': m['images']['jpg']['large_image_url'] if m.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                'release_year': m.get('published', {}).get('from', '')[:4] if m.get('published', {}).get('from') else '',
                'rating': m.get('score'),
                'pk': m.get('mal_id'),
            }
            for m in latest_resp.json().get('data', [])[:12]
        ]

        # Coming Soon: status upcoming, order by start_date ascending
        coming_soon_url = 'https://api.jikan.moe/v4/manga?status=upcoming&order_by=start_date&sort=asc'
        coming_soon_resp = requests.get(coming_soon_url)
        coming_soon = [
            {
                'title': m['title'],
                'poster_url': m['images']['jpg']['large_image_url'] if m.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                'release_year': m.get('published', {}).get('from', '')[:4] if m.get('published', {}).get('from') else '',
                'rating': m.get('score'),
                'pk': m.get('mal_id'),
            }
            for m in coming_soon_resp.json().get('data', [])[:12]
        ]
        # Fallback: If still empty, use top upcoming manga
        if not coming_soon:
            fallback_url = 'https://api.jikan.moe/v4/top/manga?type=manga&filter=upcoming'
            fallback_resp = requests.get(fallback_url)
            coming_soon = [
                {
                    'title': m['title'],
                    'poster_url': m['images']['jpg']['large_image_url'] if m.get('images', {}).get('jpg', {}).get('large_image_url') else '',
                    'release_year': m.get('published', {}).get('from', '')[:4] if m.get('published', {}).get('from') else '',
                    'rating': m.get('score'),
                    'pk': m.get('mal_id'),
                }
                for m in fallback_resp.json().get('data', [])[:12]
            ]

    except Exception:
        trending, popular, latest, coming_soon = [], [], [], []

    return render(request, 'core/content_showcase.html', {
        'type': 'manga',
        'trending': trending,
        'popular': popular,
        'latest': latest,
        'coming_soon': coming_soon,
    })

def group_staff_by_person(staff_list):
    grouped = {}
    for s in staff_list:
        key = s.get('id') or s.get('name')
        if key not in grouped:
            grouped[key] = {
                'id': s.get('id'),
                'name': s.get('name'),
                'profile_path': s.get('profile_path'),
                'jobs': [s.get('job')],
            }
        else:
            if s.get('job') not in grouped[key]['jobs']:
                grouped[key]['jobs'].append(s.get('job'))
    return list(grouped.values())

def fetch_tmdb_seasons_and_episodes(tmdb_id):
    api_key = settings.TMDB_API_KEY
    url = f'https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={api_key}&language=en-US'
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    show_data = resp.json()
    seasons = show_data.get('seasons', [])
    all_seasons = []
    for season in seasons:
        season_number = season.get('season_number')
        if season_number == 0:
            continue  # skip specials
        season_url = f'https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season_number}?api_key={api_key}&language=en-US'
        season_resp = requests.get(season_url)
        if season_resp.status_code != 200:
            continue
        season_data = season_resp.json()
        all_seasons.append({
            'season_number': season_data.get('season_number'),
            'name': season_data.get('name'),
            'overview': season_data.get('overview'),
            'poster_path': season_data.get('poster_path'),
            'episodes': season_data.get('episodes', []),
        })
    return all_seasons

def tmdb_series_detail(request, tmdb_id):
    api_key = settings.TMDB_API_KEY
    url = f'https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={api_key}&language=en-US'
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Http404("Series not found in TMDb")
    tmdb_data = resp.json()

    # Fetch credits (cast and crew)
    credits_url = f'https://api.themoviedb.org/3/tv/{tmdb_id}/credits?api_key={api_key}'
    credits_resp = requests.get(credits_url)
    credits = credits_resp.json() if credits_resp.status_code == 200 else {}
    cast = credits.get('cast', [])
    crew = credits.get('crew', [])
    grouped_staff = group_staff_by_person(crew)

    # Fetch videos
    videos_url = f'https://api.themoviedb.org/3/tv/{tmdb_id}/videos?api_key={api_key}'
    videos_resp = requests.get(videos_url)
    videos = videos_resp.json().get('results', []) if videos_resp.status_code == 200 else []

    # Fetch seasons and episodes
    seasons = fetch_tmdb_seasons_and_episodes(tmdb_id)

    # Content tracking context
    content = BaseContent.objects.filter(tmdb_id=tmdb_id, content_type='series').first()
    watchlist_entry = None
    status_choices = []
    score_labels = []
    profile_id = request.session.get('profile_id')
    if content and profile_id:
        try:
            profile = Profile.objects.get(pk=profile_id)
            watchlist_entry = Watchlist.objects.filter(profile=profile, content=content).first()
        except Profile.DoesNotExist:
            pass
        status_choices = Watchlist._meta.get_field('status').choices
        score_labels = [
            (10, "Masterpiece"), (9, "Great"), (8, "Very Good"), (7, "Good"), (6, "Fine"),
            (5, "Average"), (4, "Bad"), (3, "Very Bad"), (2, "Horrible"), (1, "Appalling"),
        ]

    return render(request, 'core/content_detail.html', {
        'content': content,
        'tmdb_data': tmdb_data,
        'related_entries': [],
        'characters': cast,
        'staff': grouped_staff,
        'themes': [],
        'videos': videos,
        'seasons': seasons,
        'watchlist_entry': watchlist_entry,
        'status_choices': status_choices,
        'score_labels': score_labels,
    })

def tmdb_movie_detail(request, tmdb_id):
    api_key = settings.TMDB_API_KEY
    url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&language=en-US'
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Http404("Movie not found in TMDb")
    tmdb_data = resp.json()

    # Fetch credits (cast and crew)
    credits_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}/credits?api_key={api_key}'
    credits_resp = requests.get(credits_url)
    credits = credits_resp.json() if credits_resp.status_code == 200 else {}
    cast = credits.get('cast', [])
    crew = credits.get('crew', [])
    grouped_staff = group_staff_by_person(crew)

    # Fetch videos
    videos_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}/videos?api_key={api_key}'
    videos_resp = requests.get(videos_url)
    videos = videos_resp.json().get('results', []) if videos_resp.status_code == 200 else []

    # Content tracking context
    content = BaseContent.objects.filter(tmdb_id=tmdb_id, content_type='movie').first()
    watchlist_entry = None
    status_choices = []
    score_labels = []
    profile_id = request.session.get('profile_id')
    if content and profile_id:
        try:
            profile = Profile.objects.get(pk=profile_id)
            watchlist_entry = Watchlist.objects.filter(profile=profile, content=content).first()
        except Profile.DoesNotExist:
            pass
        status_choices = Watchlist._meta.get_field('status').choices
        score_labels = [
            (10, "Masterpiece"), (9, "Great"), (8, "Very Good"), (7, "Good"), (6, "Fine"),
            (5, "Average"), (4, "Bad"), (3, "Very Bad"), (2, "Horrible"), (1, "Appalling"),
        ]

    print("DEBUG: content =", content)
    print("DEBUG: tmdb_data =", tmdb_data)

    return render(request, 'core/content_detail.html', {
        'content': content,
        'tmdb_data': tmdb_data,
        'related_entries': [],
        'characters': cast,
        'staff': grouped_staff,
        'themes': [],
        'videos': videos,
        'seasons': [],  # Movies don't have seasons
        'watchlist_entry': watchlist_entry,
        'status_choices': status_choices,
        'score_labels': score_labels,
    })

def update_tracking(request, pk):
    if not request.user.is_authenticated and 'profile_id' not in request.session:
        return redirect('login')
    content = get_object_or_404(BaseContent, pk=pk)
    # Get profile from session (your app uses session, not request.user)
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('login')
    profile = get_object_or_404(Profile, pk=profile_id)

    # Get or create Watchlist entry
    watchlist, created = Watchlist.objects.get_or_create(profile=profile, content=content)
    if request.method == 'POST':
        status = request.POST.get('status')
        progress = request.POST.get('progress')
        score = request.POST.get('score')
        # Validate and update fields
        if status in dict(Watchlist._meta.get_field('status').choices):
            watchlist.status = status
        try:
            watchlist.progress = int(progress)
        except (TypeError, ValueError):
            pass
        try:
            watchlist.score = int(score) if score else None
        except (TypeError, ValueError):
            pass
        watchlist.save()
        from django.contrib import messages
        messages.success(request, 'Tracking updated!')
    return redirect('content_detail', pk=content.pk)

@require_POST
def import_tmdb_content(request):
    tmdb_id = request.POST.get('tmdb_id')
    tmdb_type = request.POST.get('tmdb_type')
    if not tmdb_id or not tmdb_type:
        messages.error(request, 'Invalid TMDb import request.')
        return redirect('index')

    # Check if already exists
    content = BaseContent.objects.filter(tmdb_id=tmdb_id, content_type=tmdb_type).first()
    profile_id = request.session.get('profile_id')
    if content:
        # Also ensure a Watchlist entry exists for this user
        if profile_id:
            profile = Profile.objects.get(pk=profile_id)
            Watchlist.objects.get_or_create(profile=profile, content=content, defaults={'status': 'plan_to_watch'})
        return redirect('content_detail', pk=content.pk)

    api_key = settings.TMDB_API_KEY
    if tmdb_type == 'movie':
        url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&language=en-US'
    else:
        url = f'https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={api_key}&language=en-US'
    resp = requests.get(url)
    if resp.status_code != 200:
        messages.error(request, 'Could not fetch data from TMDb.')
        return redirect('index')
    data = resp.json()

    # Create BaseContent
    title = data.get('title') or data.get('name') or 'Untitled'
    description = data.get('overview', '')
    poster_path = data.get('poster_path')
    poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}' if poster_path else ''
    release_year = (data.get('release_date') or data.get('first_air_date') or '')[:4]
    try:
        release_year = int(release_year)
    except Exception:
        release_year = 0
    rating = data.get('vote_average', 0)

    content = BaseContent.objects.create(
        title=title,
        description=description,
        poster_url=poster_url,
        release_year=release_year,
        rating=rating,
        content_type=tmdb_type,
        tmdb_id=tmdb_id,
    )

    # Save genres from TMDB
    genres = data.get('genres', [])
    for genre in genres:
        genre_obj, _ = Genre.objects.get_or_create(name=genre['name'])
        content.genres.add(genre_obj)

    # Create Watchlist entry for this user
    if profile_id:
        profile = Profile.objects.get(pk=profile_id)
        Watchlist.objects.get_or_create(profile=profile, content=content, defaults={'status': 'plan_to_watch'})

    messages.success(request, f'Imported "{title}" to your library and added to your list!')
    return redirect('content_detail', pk=content.pk)

@require_POST
def add_to_list(request, content_id):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('login')
    try:
        profile = Profile.objects.get(pk=profile_id)
        content = BaseContent.objects.get(pk=content_id)
    except (Profile.DoesNotExist, BaseContent.DoesNotExist):
        return redirect('content_detail', pk=content_id)
    # Create watchlist entry if not exists
    Watchlist.objects.get_or_create(profile=profile, content=content)
    return redirect('content_detail', pk=content_id)