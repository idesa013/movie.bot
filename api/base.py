# api/base.py
import requests
from config_data.config import TMBD_API_KEY

TMDB_BASE_URL = "https://api.themoviedb.org/3"


def tmdb_get(endpoint: str, params: dict | None = None) -> dict:
    params = params or {}
    params["api_key"] = TMBD_API_KEY
    url = f"{TMDB_BASE_URL}/{endpoint.lstrip('/')}"
    response = requests.get(url, params=params, timeout=12)
    response.raise_for_status()
    return response.json()
