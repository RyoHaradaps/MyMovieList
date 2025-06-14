from core.models import BaseContent

BaseContent.objects.create(
    title="Iron Man",
    content_type="movie",
    genre="Action",
    release_year=2008,
    rating=8.0,
    poster_url="https://link.to/poster.jpg",
    description="A billionaire industrialist and genius inventor becomes Iron Man."
)
