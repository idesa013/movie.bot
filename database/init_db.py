from peewee import BooleanField, CharField
from playhouse.migrate import SqliteMigrator, migrate

from database.bot_config import ensure_default_bot_config
from database.models import (
    db,
    User,
    FavoriteMovie,
    FavoriteActor,
    FavoriteDirector,
    BotConfig,
    MovieSearchLog,
    ActorSearchLog,
    DirectorSearchLog,
    UserMessage,
    UserBlockLog,
)


def _table_exists(table_name: str) -> bool:
    return db.table_exists(table_name)


def _column_exists(table_name: str, column_name: str) -> bool:
    return any(column.name == column_name for column in db.get_columns(table_name))


def init_db():
    db.connect(reuse_if_open=True)

    migrator = SqliteMigrator(db)

    db.create_tables(
        [
            User,
            FavoriteMovie,
            FavoriteActor,
            FavoriteDirector,
            BotConfig,
            MovieSearchLog,
            ActorSearchLog,
            DirectorSearchLog,
            UserMessage,
            UserBlockLog,
        ],
        safe=True,
    )

    if _table_exists("user") and not _column_exists("user", "language"):
        migrate(migrator.add_column("user", "language", CharField(default="en")))

    if _table_exists("user") and not _column_exists("user", "active"):
        migrate(migrator.add_column("user", "active", BooleanField(default=True)))

    if _table_exists("search_log") and not _table_exists("movie_search_log"):
        migrate(migrator.rename_table("search_log", "movie_search_log"))

    if _table_exists("movie_search_log") and not _column_exists(
        "movie_search_log", "searched_from"
    ):
        migrate(
            migrator.add_column(
                "movie_search_log",
                "searched_from",
                CharField(default="movie"),
            )
        )

    if _table_exists("actor_search_log") and not _column_exists(
        "actor_search_log", "searched_from"
    ):
        migrate(
            migrator.add_column(
                "actor_search_log",
                "searched_from",
                CharField(default="str"),
            )
        )

    if _table_exists("director_search_log") and not _column_exists(
        "director_search_log", "searched_from"
    ):
        migrate(
            migrator.add_column(
                "director_search_log",
                "searched_from",
                CharField(default="str"),
            )
        )

    if _table_exists("msg_from_user") and not _column_exists(
        "msg_from_user", "created_at"
    ):
        migrate(
            migrator.add_column(
                "msg_from_user",
                "created_at",
                CharField(default=""),
            )
        )

    MovieSearchLog.update(
        searched_from="movie",
    ).where(MovieSearchLog.searched_from.in_(("str", "straight", "movie"))).execute()

    MovieSearchLog.update(
        searched_from="actor",
    ).where(MovieSearchLog.searched_from.in_(("fav", "actor"))).execute()

    MovieSearchLog.update(
        searched_from="director",
    ).where(MovieSearchLog.searched_from.in_(("dir", "director"))).execute()

    UserMessage.update(created_at="").where(UserMessage.created_at.is_null()).execute()

    ensure_default_bot_config()
    db.close()
