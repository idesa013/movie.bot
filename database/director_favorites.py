from database.models import FavoriteDirector


def add_director_favorite(user_id: int, director_id: int, search_time: str) -> None:
    FavoriteDirector.get_or_create(
        user_id=user_id,
        director_id=director_id,
        defaults={"search_time": search_time},
    )


def check_director_favorite(user_id: int, director_id: int) -> bool:
    return (
        FavoriteDirector.select()
        .where(
            (FavoriteDirector.user_id == user_id)
            & (FavoriteDirector.director_id == director_id)
        )
        .exists()
    )


def remove_director_favorite(user_id: int, director_id: int) -> None:
    (
        FavoriteDirector.delete()
        .where(
            (FavoriteDirector.user_id == user_id)
            & (FavoriteDirector.director_id == director_id)
        )
        .execute()
    )
