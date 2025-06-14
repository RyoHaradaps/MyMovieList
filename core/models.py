from django.db import models

# Profile model for user registration/authentication
class Profile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # NOTE: Use hashed passwords in production!
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


# Unified model for Movie, Series, MiniSeries, etc.
class BaseContent(models.Model):
    CONTENT_TYPES = [
        ('movie', 'Movie'),
        ('series', 'Series'),
        ('miniseries', 'MiniSeries'),
        ('animatedshow', 'Animated Show'),
        ('comic', 'Cartoon Comic'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    poster_url = models.URLField(blank=True)
    genre = models.CharField(max_length=100)
    rating = models.FloatField(default=0)
    release_year = models.IntegerField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-release_year']

    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"

class Watchlist(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.ForeignKey(BaseContent, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
