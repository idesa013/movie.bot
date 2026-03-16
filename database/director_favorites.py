from database._favorites_base import (
    add_favorite_record,
    check_favorite_record,
    remove_favorite_record,
)
from database.models import FavoriteDirector


def add_director_favorite(user_id: int, director_id: int, search_time: str) -> None:
    add_favorite_record(
        FavoriteDirector,
        user_id=user_id,
        director_id=director_id,
        defaults={"search_time": search_time},
    )


def check_director_favorite(user_id: int, director_id: int) -> bool:
    return check_favorite_record(
        FavoriteDirector,
        user_id=user_id,
        director_id=director_id,
    )


def remove_director_favorite(user_id: int, director_id: int) -> None:
    remove_favorite_record(
        FavoriteDirector,
        user_id=user_id,
        director_id=director_id,
    )
