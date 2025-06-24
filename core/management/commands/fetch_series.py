for series in tmdb_results:
    tmdb_id = series['id']
    title = series['name']
    # ...other fields...
            BaseContent.objects.update_or_create(
        tmdb_id=tmdb_id,
                content_type='series',
                defaults={
            'title': title,
            'description': series.get('overview', ''),
            'poster_url': f"https://image.tmdb.org/t/p/w500{series['poster_path']}" if series.get('poster_path') else '',
            'release_year': int(series.get('first_air_date', '0000')[:4]) if series.get('first_air_date') else 0,
            'rating': series.get('vote_average', 0),
            # ...other fields...
        }
    ) 