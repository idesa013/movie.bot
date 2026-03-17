def normalize_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def pick_exact_or_first(results: list[dict], query: str) -> dict | None:
    normalized_query = normalize_text(query)

    for item in results:
        title = normalize_text(item.get("title", ""))
        original_title = normalize_text(item.get("original_title", ""))

        if normalized_query == title or normalized_query == original_title:
            return item

    return results[0] if results else None


def pick_best_person_result(
    results: list[dict],
    query: str,
    department: str,
    validator,
    tmdb_lang: str,
    limit: int = 12,
) -> int | None:
    normalized_query = normalize_text(query)

    persons = [
        person for person in results if person.get("known_for_department") == department
    ]

    exact_matches = []
    for person in persons:
        name = normalize_text(person.get("name", ""))
        original_name = normalize_text(person.get("original_name", ""))

        if normalized_query == name or normalized_query == original_name:
            exact_matches.append(person)

    exact_matches.sort(key=lambda item: item.get("popularity", 0), reverse=True)

    for person in exact_matches:
        person_id = person.get("id")
        if not person_id:
            continue
        if validator(int(person_id), tmdb_lang):
            return int(person_id)

    persons.sort(key=lambda item: item.get("popularity", 0), reverse=True)

    for person in persons[:limit]:
        person_id = person.get("id")
        if not person_id:
            continue
        if validator(int(person_id), tmdb_lang):
            return int(person_id)

    return None
