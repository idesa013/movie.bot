import requests
from config_data.config import TMBD_API_KEY

BASE_URL = "https://api.themoviedb.org/3"


def tmdb_get(endpoint: str, params: dict | None = None) -> dict:
    if params is None:
        params = {}
    params["api_key"] = TMBD_API_KEY
    params.setdefault("language", "ru-RU")
    url = f"{BASE_URL}/{endpoint}"
    r = requests.get(url, params=params, timeout=12)
    r.raise_for_status()
    return r.json()


def _split_lang(language: str) -> tuple[str, str]:
    if not language:
        return ("en", "US")
    parts = language.split("-")
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""


def _get_person_bio_from_translations(person_id: int, language: str) -> str | None:
    data = tmdb_get(f"person/{person_id}/translations", params={"language": "en-US"})
    translations = data.get("translations") or []
    iso_639, iso_3166 = _split_lang(language)

    for tr in translations:
        if tr.get("iso_639_1") == iso_639 and (
            not iso_3166 or tr.get("iso_3166_1") == iso_3166
        ):
            bio = ((tr.get("data") or {}).get("biography") or "").strip()
            if bio:
                return bio

    for tr in translations:
        if tr.get("iso_639_1") == iso_639:
            bio = ((tr.get("data") or {}).get("biography") or "").strip()
            if bio:
                return bio

    return None


def search_director(query: str, language: str | None = None) -> dict:
    params = {"query": query}
    if language:
        params["language"] = language
    return tmdb_get("search/person", params=params)


def get_director_details(director_id: int, language: str = "ru-RU") -> dict:
    data = tmdb_get(f"person/{director_id}", params={"language": language})

    bio = _get_person_bio_from_translations(director_id, language)
    if bio:
        data["biography"] = bio
        data["_bio_lang"] = language
        return data

    bio_raw = (data.get("biography") or "").strip()
    if language.startswith("ru") and not bio_raw:
        bio_en = _get_person_bio_from_translations(director_id, "en-US")
        if bio_en:
            data["biography"] = bio_en
            data["_bio_fallback_lang"] = "en"
            data["_bio_lang"] = "en-US"

    return data


def get_director_movie_credits(director_id: int, language: str = "ru-RU") -> dict:
    return tmdb_get(
        f"person/{director_id}/movie_credits", params={"language": language}
    )
