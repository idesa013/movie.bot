from database.models import FavoriteActor


def add_actor_favorite(user_id: int, actor_id: int, search_time: str) -> None:
    FavoriteActor.get_or_create(
        user_id=user_id,
        actor_id=actor_id,
        defaults={"search_time": search_time},
    )


def check_actor_favorite(user_id: int, actor_id: int) -> bool:
    return (
        FavoriteActor.select()
        .where(
            (FavoriteActor.user_id == user_id) & (FavoriteActor.actor_id == actor_id)
        )
        .exists()
    )


def remove_actor_favorite(user_id: int, actor_id: int) -> None:
    (
        FavoriteActor.delete()
        .where(
            (FavoriteActor.user_id == user_id) & (FavoriteActor.actor_id == actor_id)
        )
        .execute()
    )
