from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import BaseContent, Profile, Watchlist
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.
def index(request):
    profile = None
    profile_id = request.session.get('profile_id')
    if profile_id:
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            profile = None
    trending = BaseContent.objects.filter(content_type='movie')[:5]
    top_airing = BaseContent.objects.filter(content_type='tv')[:5]
    latest_episodes = BaseContent.objects.filter(content_type='episode')[:5]
    upcoming = BaseContent.objects.filter(content_type='movie')[:5]
    top_rated = BaseContent.objects.filter(content_type='movie')[:5]
    featured = BaseContent.objects.filter(content_type='movie')[:5]
    watchlist_ids = []
    if profile:
        watchlist = Watchlist.objects.filter(profile=profile)
        watchlist_ids = [item.content_id for item in watchlist]
    context = {
        'trending': trending,
        'top_airing': top_airing,
        'latest_episodes': latest_episodes,
        'upcoming': upcoming,
        'top_rated': top_rated,
        'featured': featured,
        'watchlist_ids': watchlist_ids,
        'notification_count': 0,  # Set to 0 for now; update with real count later
    }
    return render(request, 'core/index.html', context)

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
    return redirect('login')

def home_view(request):
    profile_id = request.session.get('profile_id')
    if not profile_id:
        messages.error(request, "You must be logged in to view this page.")
        return redirect('login')
    profile = Profile.objects.get(id=profile_id)
    return render(request, 'core/index.html', {'profile': profile, 'movies': []})

def search(request):
    # Dummy implementation, just renders the index page for now
    return render(request, 'core/index.html', {'movies': []})

def movies_view(request):
    movies = BaseContent.objects.filter(content_type='movie')
    return render(request, 'core/movies.html', {'movies': movies})

def profile(request, username):
    profile = get_object_or_404(Profile, username=username)
    watchlist = Watchlist.objects.filter(profile=profile)

    # Content stats (movies, series, miniseries, animatedshow)
    content_types = ['movie', 'series', 'miniseries', 'animatedshow']
    stats = {
        'watching': watchlist.filter(content__content_type__in=content_types, content__genre__icontains='watching').count(),
        'completed': watchlist.filter(content__content_type__in=content_types, content__genre__icontains='completed').count(),
        'on_hold': watchlist.filter(content__content_type__in=content_types, content__genre__icontains='on-hold').count(),
        'dropped': watchlist.filter(content__content_type__in=content_types, content__genre__icontains='dropped').count(),
        'plan_to_watch': watchlist.filter(content__content_type__in=content_types, content__genre__icontains='plan').count(),
        'total': watchlist.filter(content__content_type__in=content_types).count(),
    }

    # Comic stats
    comic_stats = {
        'reading': watchlist.filter(content__content_type='comic', content__genre__icontains='reading').count(),
        'completed': watchlist.filter(content__content_type='comic', content__genre__icontains='completed').count(),
        'on_hold': watchlist.filter(content__content_type='comic', content__genre__icontains='on-hold').count(),
        'dropped': watchlist.filter(content__content_type='comic', content__genre__icontains='dropped').count(),
        'plan_to_read': watchlist.filter(content__content_type='comic', content__genre__icontains='plan').count(),
        'total': watchlist.filter(content__content_type='comic').count(),
    }

    # Last content updates (not comics)
    last_content_updates = watchlist.filter(content__content_type__in=content_types).order_by('-added_on')[:5]
    last_content_updates = [w.content for w in last_content_updates]

    # Last comic updates
    last_comic_updates = watchlist.filter(content__content_type='comic').order_by('-added_on')[:5]
    last_comic_updates = [w.content for w in last_comic_updates]

    context = {
        'profile': profile,
        'watchlist': watchlist,
        'stats': stats,
        'comic_stats': comic_stats,
        'last_content_updates': last_content_updates,
        'last_comic_updates': last_comic_updates,
    }
    return render(request, 'core/profile.html', context)