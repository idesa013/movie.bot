from database.models import MovieSearchLog, ActorSearchLog, DirectorSearchLog


def log_movie_search(
    user_id: int,
    movie_id: int,
    search_time: str,
    genre_ids: str = "",
    searched_from: str = "movie",
) -> None:
    MovieSearchLog.create(
        user_id=user_id,
        movie_id=movie_id,
        search_time=search_time,
        genre_ids=genre_ids,
        searched_from=searched_from,
    )


def log_actor_search(
    user_id: int,
    actor_id: int,
    search_time: str,
    searched_from: str = "str",
) -> None:
    ActorSearchLog.create(
        user_id=user_id,
        actor_id=actor_id,
        search_time=search_time,
        searched_from=searched_from,
    )


def log_director_search(
    user_id: int,
    director_id: int,
    search_time: str,
    searched_from: str = "str",
) -> None:
    DirectorSearchLog.create(
        user_id=user_id,
        director_id=director_id,
        search_time=search_time,
        searched_from=searched_from,
    )
