from django.contrib import admin
from .models import BaseContent, ContentRelation
# Register your models here.


@admin.register(BaseContent)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'genre', 'release_year', 'rating']
    search_fields = ['title', 'genre']

admin.site.register(ContentRelation)
