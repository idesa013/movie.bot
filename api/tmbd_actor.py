import requests
from config_data.config import TMBD_API_KEY


BASE_URL = "https://api.themoviedb.org/3"


def search_actor(query: str):
    url = f"{BASE_URL}/search/person"
    params = {
        "api_key": TMBD_API_KEY,
        "query": query,
        "language": "ru-RU",
    }
    return requests.get(url, params=params).json()


def get_actor_details(actor_id: int):
    url = f"{BASE_URL}/person/{actor_id}"
    params = {
        "api_key": TMBD_API_KEY,
        "language": "ru-RU",
    }
    return requests.get(url, params=params).json()


def get_actor_movie_credits(actor_id: int):
    url = f"{BASE_URL}/person/{actor_id}/movie_credits"
    params = {
        "api_key": TMBD_API_KEY,
        "language": "ru-RU",
    }
    return requests.get(url, params=params).json()
