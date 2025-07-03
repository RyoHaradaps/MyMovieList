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


# Genre model
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Unified model for Movie, Series, MiniSeries, etc.
class BaseContent(models.Model):
    CONTENT_TYPES = [
        ('movie', 'Movie'),
        ('series', 'Series'),
        ('animatedshow', 'Animated Show'),
        ('comic', 'Cartoon Comic'),
    ]

    title = models.CharField(max_length=255)
    alt_title = models.CharField(max_length=255, blank=True, null=True)  # e.g., Japanese/English alt title
    synonyms = models.TextField(blank=True, null=True)  # Comma-separated or list of synonyms
    description = models.TextField(blank=True)
    poster_url = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    rating = models.FloatField(default=0)
    release_year = models.IntegerField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    tmdb_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-release_year']

    def __str__(self):
        return self.title

class Watchlist(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.ForeignKey(BaseContent, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('on_hold', 'On-Hold'),
        ('dropped', 'Dropped'),
        ('plan_to_watch', 'Plan to Watch/Read'),
    ], default='plan_to_watch')
    score = models.IntegerField(null=True, blank=True)
    progress = models.IntegerField(default=0)
    review = models.TextField(blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    rewatched = models.IntegerField(default=0)  # for movies/series
    reread = models.IntegerField(default=0)     # for comics

class ContentRelation(models.Model):
    RELATION_CHOICES = [
        ('prequel', 'Prequel'),
        ('sequel', 'Sequel'),
        ('adaptation', 'Adaptation'),
        ('side_story', 'Side Story'),
        ('parent_story', 'Parent Story'),
        # Add more as needed
    ]
    from_content = models.ForeignKey(BaseContent, related_name='from_relations', on_delete=models.CASCADE)
    to_content = models.ForeignKey(BaseContent, related_name='to_relations', on_delete=models.CASCADE)
    relation_type = models.CharField(max_length=20, choices=RELATION_CHOICES)

    def __str__(self):
        return f"{self.from_content.title} ({self.get_relation_type_display()}) {self.to_content.title}"

# Character model linked to BaseContent
class Character(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=[('main', 'Main'), ('supporting', 'Supporting')], default='supporting')
    content = models.ForeignKey(BaseContent, related_name='characters', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.content.title})"

# Voice Actor model
class VoiceActor(models.Model):
    name = models.CharField(max_length=100)
    language = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    characters = models.ManyToManyField(Character, related_name='voice_actors', blank=True)

    def __str__(self):
        return self.name

# Staff model linked to BaseContent
class Staff(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    content = models.ForeignKey(BaseContent, related_name='staff', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.role})"

# Theme model for Opening/Ending themes
class Theme(models.Model):
    THEME_TYPES = [
        ('opening', 'Opening'),
        ('ending', 'Ending'),
    ]
    content = models.ForeignKey(BaseContent, related_name='themes', on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=THEME_TYPES)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.get_type_display()} Theme: {self.title} ({self.content.title})"
