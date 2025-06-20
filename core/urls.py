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
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
    path('movies/list/', views.movie_list, name='movie_list'),
    path('series/list/', views.series_list, name='series_list'),
    path('animated/list/', views.animated_list, name='animated_list'),
    path('anime/list/', views.anime_list, name='anime_list'),
    path('manga/list/', views.manga_list, name='manga_list'),
    path('comics/list/', views.comic_list, name='comic_list'),
    path('content/<int:pk>/', views.content_detail, name='content_detail'),
    path('movies/', views.movies_showcase, name='movies_showcase'),
    path('series/', views.series_showcase, name='series_showcase'),
    path('anime/', views.anime_showcase, name='anime_showcase'),
    path('comics/', views.comics_showcase, name='comics_showcase'),
    path('manga/', views.manga_showcase, name='manga_showcase'),
    path('animated/', views.animated_showcase, name='animated_showcase'),
]
