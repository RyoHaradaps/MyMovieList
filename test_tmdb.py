import requests

url = "https://api.themoviedb.org/3/tv/popular?api_key=28d27a694a324a1f8c2c0a869b2f7065&language=en-US&page=1"
headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyMovieListBot/1.0)'}
print(requests.get(url, headers=headers).text)
