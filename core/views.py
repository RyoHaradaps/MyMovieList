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
    return render(request, 'core/index.html', {'profile': profile, 'movies': []})

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
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, username=username)
    watchlist = Watchlist.objects.filter(profile=profile)
    context = {
        'profile': profile,
        'watchlist': watchlist,
    }
    return render(request, 'core/profile.html', context)