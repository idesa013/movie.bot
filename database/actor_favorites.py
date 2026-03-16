from database._favorites_base import (
    add_favorite_record,
    check_favorite_record,
    remove_favorite_record,
)
from database.models import FavoriteActor


def add_actor_favorite(user_id: int, actor_id: int, search_time: str) -> None:
    add_favorite_record(
        FavoriteActor,
        user_id=user_id,
        actor_id=actor_id,
        defaults={"search_time": search_time},
    )


def check_actor_favorite(user_id: int, actor_id: int) -> bool:
    return check_favorite_record(
        FavoriteActor,
        user_id=user_id,
        actor_id=actor_id,
    )


def remove_actor_favorite(user_id: int, actor_id: int) -> None:
    remove_favorite_record(
        FavoriteActor,
        user_id=user_id,
        actor_id=actor_id,
    )
