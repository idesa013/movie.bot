import requests
from config_data.config import TMBD_API_KEY

BASE_URL = "https://api.themoviedb.org/3"


def tmdb_get(endpoint: str, params: dict = None) -> dict:
    """
    Универсальная функция для GET-запросов к TMDB API
    """
    if params is None:
        params = {}
    params["api_key"] = TMBD_API_KEY
    params["language"] = "ru-RU"
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()  # чтобы падало при ошибке HTTP
    return response.json()


# Теперь твои функции можно переписать так:


def get_movie_details(movie_id: int) -> dict:
    return tmdb_get(f"movie/{movie_id}")


def get_movie_credits(movie_id: int) -> dict:
    return tmdb_get(f"movie/{movie_id}/credits")
