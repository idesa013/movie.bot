import requests
from config_data.config import TMBD_API_KEY

BASE_URL = "https://api.themoviedb.org/3"


def tmdb_get(endpoint: str, params: dict | None = None) -> dict:
    if params is None:
        params = {}
    params["api_key"] = TMBD_API_KEY
    params.setdefault("language", "ru-RU")
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, params=params, timeout=12)
    response.raise_for_status()
    return response.json()


def get_movie_details(movie_id: int, language: str | None = None) -> dict:
    params = {}
    if language:
        params["language"] = language
    return tmdb_get(f"movie/{movie_id}", params=params)


def get_movie_credits(movie_id: int, language: str | None = None) -> dict:
    params = {}
    if language:
        params["language"] = language
    return tmdb_get(f"movie/{movie_id}/credits", params=params)


def search_movie(query: str, language: str | None = None) -> dict:
    params = {"query": query}
    if language:
        params["language"] = language
    return tmdb_get("search/movie", params=params)


def discover_movies_by_genre(
    genre_id: int,
    language: str | None = None,
    page: int = 1,
    sort_by: str = "popularity.desc",
    vote_average_gte: float = 4,
) -> dict:
    params = {
        "sort_by": sort_by,
        "with_genres": str(genre_id),
        "include_adult": "false",
        "include_video": "false",
        "vote_average.gte": str(vote_average_gte),
        "page": page,
    }
    if language:
        params["language"] = language
    return tmdb_get("discover/movie", params=params)


def discover_new_movies(
    language: str | None = None,
    page: int = 1,
    vote_average_gte: float = 4,
) -> dict:
    params = {
        "sort_by": "primary_release_date.desc",
        "include_adult": "false",
        "include_video": "false",
        "vote_average.gte": str(vote_average_gte),
        "page": page,
    }
    if language:
        params["language"] = language
    return tmdb_get("discover/movie", params=params)