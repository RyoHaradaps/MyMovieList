from core.models import BaseContent, Genre

# Create a genre first
genre, created = Genre.objects.get_or_create(name="Action")

# Create the content
BaseContent.objects.create(
    title="Iron Man",
    content_type="movie",
    release_year=2008,
    rating=8.0,
    poster_url="https://link.to/poster.jpg",
    description="A billionaire industrialist and genius inventor becomes Iron Man."
)
