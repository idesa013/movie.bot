from __future__ import annotations

from typing import Any

from database.models import (
    MovieSearchLog,
    ActorSearchLog,
    DirectorSearchLog,
    FavoriteMovie,
    FavoriteActor,
    FavoriteDirector,
)


def _favorite_movie_ids(user_id: int) -> set[int]:
    return {
        row.movie_id
        for row in FavoriteMovie.select(FavoriteMovie.movie_id).where(
            FavoriteMovie.user_id == user_id
        )
    }


def _favorite_actor_ids(user_id: int) -> set[int]:
    return {
        row.actor_id
        for row in FavoriteActor.select(FavoriteActor.actor_id).where(
            FavoriteActor.user_id == user_id
        )
    }


def _favorite_director_ids(user_id: int) -> set[int]:
    return {
        row.director_id
        for row in FavoriteDirector.select(FavoriteDirector.director_id).where(
            FavoriteDirector.user_id == user_id
        )
    }


def get_user_history(user_id: int, limit: int = 20) -> list[dict[str, Any]]:
    fav_movie_ids = _favorite_movie_ids(user_id)
    fav_actor_ids = _favorite_actor_ids(user_id)
    fav_director_ids = _favorite_director_ids(user_id)

    rows: list[dict[str, Any]] = []

    movie_logs = (
        MovieSearchLog.select(
            MovieSearchLog.movie_id,
            MovieSearchLog.search_time,
            MovieSearchLog.searched_from,
        )
        .where(MovieSearchLog.user_id == user_id)
        .order_by(MovieSearchLog.search_time.desc())
        .limit(limit)
    )
    for row in movie_logs:
        rows.append(
            {
                "search_time": row.search_time,
                "entity_type": "movie",
                "entity_id": row.movie_id,
                "searched_from": row.searched_from or "movie",
                "in_favorites": row.movie_id in fav_movie_ids,
            }
        )

    actor_logs = (
        ActorSearchLog.select(
            ActorSearchLog.actor_id,
            ActorSearchLog.search_time,
            ActorSearchLog.searched_from,
        )
        .where(ActorSearchLog.user_id == user_id)
        .order_by(ActorSearchLog.search_time.desc())
        .limit(limit)
    )
    for row in actor_logs:
        rows.append(
            {
                "search_time": row.search_time,
                "entity_type": "actor",
                "entity_id": row.actor_id,
                "searched_from": row.searched_from or "actor",
                "in_favorites": row.actor_id in fav_actor_ids,
            }
        )

    director_logs = (
        DirectorSearchLog.select(
            DirectorSearchLog.director_id,
            DirectorSearchLog.search_time,
            DirectorSearchLog.searched_from,
        )
        .where(DirectorSearchLog.user_id == user_id)
        .order_by(DirectorSearchLog.search_time.desc())
        .limit(limit)
    )
    for row in director_logs:
        rows.append(
            {
                "search_time": row.search_time,
                "entity_type": "director",
                "entity_id": row.director_id,
                "searched_from": row.searched_from or "director",
                "in_favorites": row.director_id in fav_director_ids,
            }
        )

    rows.sort(key=lambda x: x["search_time"], reverse=False)
    return rows[:limit]
