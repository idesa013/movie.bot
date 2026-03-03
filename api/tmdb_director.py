import requests
from config_data.config import TMBD_API_KEY

BASE_URL = "https://api.themoviedb.org/3"


def tmdb_get(endpoint: str, params: dict = None) -> dict:
    if params is None:
        params = {}
    params["api_key"] = TMBD_API_KEY
    params.setdefault("language", "ru-RU")
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def search_director(query: str) -> dict:
    # TMDB не имеет отдельного поиска режиссёров — это person search.
    return tmdb_get("search/person", params={"query": query})


def get_director_details(director_id: int) -> dict:
    return tmdb_get(f"person/{director_id}")


def get_director_movie_credits(director_id: int) -> dict:
    return tmdb_get(f"person/{director_id}/movie_credits")
