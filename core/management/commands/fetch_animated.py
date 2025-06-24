for show in tmdb_results:
    tmdb_id = show['id']
    title = show['name']
    # ...other fields...
            BaseContent.objects.update_or_create(
        tmdb_id=tmdb_id,
                content_type='animatedshow',
                defaults={
            'title': title,
            'description': show.get('overview', ''),
            'poster_url': f"https://image.tmdb.org/t/p/w500{show['poster_path']}" if show.get('poster_path') else '',
            'release_year': int(show.get('first_air_date', '0000')[:4]) if show.get('first_air_date') else 0,
            'rating': show.get('vote_average', 0),
            # ...other fields...
        }
    ) 