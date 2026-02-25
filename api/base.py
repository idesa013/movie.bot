import requests
from config_data.config import TMBD_API_KEY

BASE_URL = "https://api.themoviedb.org/3"


def make_request(endpoint: str, params: dict | None = None):
    url = f"{BASE_URL}{endpoint}"

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
