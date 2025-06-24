from django.contrib import admin
from .models import BaseContent, ContentRelation, Profile, Watchlist, Genre, Character, VoiceActor, Staff, Theme
# Register your models here.


@admin.register(BaseContent)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'display_genres', 'release_year', 'rating']
    search_fields = ['title', 'genres__name']

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    display_genres.short_description = 'Genres'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'join_date', 'last_online']
    search_fields = ['username', 'email']

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['profile', 'content', 'status', 'score', 'progress']
    list_filter = ['status', 'content__content_type']

admin.site.register(ContentRelation)
admin.site.register(Genre)
admin.site.register(Character)
admin.site.register(VoiceActor)
admin.site.register(Staff)
admin.site.register(Theme)
