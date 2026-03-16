from database.models import FavoriteMovie


def add_favorite(
    user_id: int, movie_id: int, search_time: str, genre_ids: str = ""
) -> None:
    FavoriteMovie.get_or_create(
        user_id=user_id,
        movie_id=movie_id,
        defaults={
            "search_time": search_time,
            "genre_ids": genre_ids,
        },
    )


def check_favorite(user_id: int, movie_id: int) -> bool:
    return (
        FavoriteMovie.select()
        .where(
            (FavoriteMovie.user_id == user_id) & (FavoriteMovie.movie_id == movie_id)
        )
        .exists()
    )


def remove_favorite(user_id: int, movie_id: int) -> None:
    (
        FavoriteMovie.delete()
        .where(
            (FavoriteMovie.user_id == user_id) & (FavoriteMovie.movie_id == movie_id)
        )
        .execute()
    )
