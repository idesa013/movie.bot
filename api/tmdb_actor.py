from api.base import tmdb_get


def _split_lang(language: str) -> tuple[str, str]:
    # "en-US" -> ("en","US"), "ru-RU" -> ("ru","RU")
    if not language:
        return ("en", "US")
    parts = language.split("-")
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""


def _get_person_bio_from_translations(person_id: int, language: str) -> str | None:
    """
    Надёжно вытаскиваем биографию из /person/{id}/translations.
    Это нужно, потому что person/{id}?language=... не всегда возвращает нужный перевод.
    """
    data = tmdb_get(f"person/{person_id}/translations", params={"language": "en-US"})
    translations = data.get("translations") or []
    iso_639, iso_3166 = _split_lang(language)

    # сначала точное совпадение (en + US)
    for tr in translations:
        if tr.get("iso_639_1") == iso_639 and (
            not iso_3166 or tr.get("iso_3166_1") == iso_3166
        ):
            bio = ((tr.get("data") or {}).get("biography") or "").strip()
            if bio:
                return bio

    # потом просто совпадение по языку (en)
    for tr in translations:
        if tr.get("iso_639_1") == iso_639:
            bio = ((tr.get("data") or {}).get("biography") or "").strip()
            if bio:
                return bio

    return None


def search_actor(query: str, language: str | None = None) -> dict:
    params = {"query": query}
    if language:
        params["language"] = language
    return tmdb_get("search/person", params=params)


def get_actor_details(actor_id: int, language: str = "ru-RU") -> dict:
    data = tmdb_get(f"person/{actor_id}", params={"language": language})

    # 1) пробуем translations для требуемого языка
    bio = _get_person_bio_from_translations(actor_id, language)
    if bio:
        data["biography"] = bio
        data["_bio_lang"] = language
        return data

    # 2) если русский и пусто — fallback на EN (как было)
    bio_raw = (data.get("biography") or "").strip()
    if language.startswith("ru") and not bio_raw:
        bio_en = _get_person_bio_from_translations(actor_id, "en-US")
        if bio_en:
            data["biography"] = bio_en
            data["_bio_fallback_lang"] = "en"
            data["_bio_lang"] = "en-US"

    return data


def get_actor_movie_credits(actor_id: int, language: str = "ru-RU") -> dict:
    return tmdb_get(f"person/{actor_id}/movie_credits", params={"language": language})
