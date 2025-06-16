from django.db import models

# Profile model for user registration/authentication
class Profile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # NOTE: Use hashed passwords in production!
    birthday = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True)
    last_online = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


# Unified model for Movie, Series, MiniSeries, etc.
class BaseContent(models.Model):
    CONTENT_TYPES = [
        ('movie', 'Movie'),
        ('series', 'Series'),
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
    status = models.CharField(max_length=20, choices=[
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('on_hold', 'On-Hold'),
        ('dropped', 'Dropped'),
        ('plan', 'Plan to Watch/Read'),
    ], default='plan')
    score = models.IntegerField(null=True, blank=True)
    progress = models.IntegerField(default=0)
    review = models.TextField(blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    rewatched = models.IntegerField(default=0)  # for movies/series
    reread = models.IntegerField(default=0)     # for comics
