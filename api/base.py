# api/base.py
import requests
from config_data.config import TMDB_BASE_URL, TMBD_API_KEY


def tmdb_get(endpoint: str, params: dict | None = None) -> dict:
    params = params or {}
    params["api_key"] = TMBD_API_KEY
    url = f"{TMDB_BASE_URL}/{endpoint.lstrip('/')}"
    response = requests.get(url, params=params, timeout=12)
    response.raise_for_status()
    return response.json()


def make_request(endpoint: str, params: dict | None = None):
    url = f"{TMDB_BASE_URL}{endpoint}"

    if params is None:
        params = {}

    params["api_key"] = TMBD_API_KEY
    params["language"] = "ru-RU"

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"TMDB API error: {response.status_code} - {response.text}")
            return None

        return response.json()

    except requests.RequestException as e:
        print(f"TMDB connection error: {e}")
        return None
