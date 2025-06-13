from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # This will show index.html at the root URL
    path('home/', views.home_view, name='home'),  # Move home_view to /home/
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search, name='search'),  # <-- Add this line
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),  # <-- Add this line
    # path('movies/', views.movies, name='movies'),
    # path('series/', views.series, name='series'),
    # path('watchlist/', views.watchlist, name='watchlist'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search, name='search'),
]
