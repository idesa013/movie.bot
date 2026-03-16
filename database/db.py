from peewee import SqliteDatabase

from config_data.config import DB_PATH

db = SqliteDatabase(DB_PATH)


def init_db():
    from database.models import (
        User,
        FavoriteMovie,
        FavoriteActor,
        FavoriteDirector,
        BotConfig,
    )
    from database.bot_config import ensure_default_bot_config

    db.connect(reuse_if_open=True)

    db.create_tables(
        [
            User,
            FavoriteMovie,
            FavoriteActor,
            FavoriteDirector,
            BotConfig,
        ],
        safe=True,
    )

    ensure_default_bot_config()

    db.close()
