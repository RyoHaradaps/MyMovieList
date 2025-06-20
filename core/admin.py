from django.contrib import admin
from .models import BaseContent, ContentRelation
# Register your models here.


@admin.register(BaseContent)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'display_genres', 'release_year', 'rating']
    search_fields = ['title', 'genres__name']

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    display_genres.short_description = 'Genres'

admin.site.register(ContentRelation)
