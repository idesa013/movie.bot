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
    params.setdefault("language", "ru-RU")  # по умолчанию русский язык
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


# Переписанные функции
def search_actor(query: str) -> dict:
    return tmdb_get("search/person", params={"query": query})


def get_actor_details(actor_id: int) -> dict:
    return tmdb_get(f"person/{actor_id}")


def get_actor_movie_credits(actor_id: int) -> dict:
    return tmdb_get(f"person/{actor_id}/movie_credits")
