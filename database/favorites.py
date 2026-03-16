from database._favorites_base import (
    add_favorite_record,
    check_favorite_record,
    remove_favorite_record,
)
from database.models import FavoriteMovie


def add_favorite(
    user_id: int,
    movie_id: int,
    search_time: str,
    genre_ids: str = "",
) -> None:
    add_favorite_record(
        FavoriteMovie,
        user_id=user_id,
        movie_id=movie_id,
        defaults={
            "search_time": search_time,
            "genre_ids": genre_ids,
        },
    )


def check_favorite(user_id: int, movie_id: int) -> bool:
    return check_favorite_record(
        FavoriteMovie,
        user_id=user_id,
        movie_id=movie_id,
    )


def remove_favorite(user_id: int, movie_id: int) -> None:
    remove_favorite_record(
        FavoriteMovie,
        user_id=user_id,
        movie_id=movie_id,
    )
