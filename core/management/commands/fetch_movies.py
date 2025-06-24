for movie in tmdb_results:
    tmdb_id = movie['id']
    title = movie['title']
    # ...other fields...
            BaseContent.objects.update_or_create(
        tmdb_id=tmdb_id,
                content_type='movie',
                defaults={
            'title': title,
            'description': movie.get('overview', ''),
            'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else '',
            'release_year': int(movie.get('release_date', '0000')[:4]) if movie.get('release_date') else 0,
            'rating': movie.get('vote_average', 0),
            # ...other fields...
        }
    ) 