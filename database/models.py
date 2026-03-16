from datetime import datetime

from peewee import (
    Model,
    SqliteDatabase,
    IntegerField,
    CharField,
    DateTimeField,
    BooleanField,
)

from database.db import DB_PATH

db = SqliteDatabase(DB_PATH)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(unique=True)
    username = CharField(null=True)
    name = CharField()
    surname = CharField(null=True)
    age = IntegerField()
    email = CharField()
    phone_number = CharField()
    reg_date = DateTimeField(default=datetime.now)
    language = CharField(default="en")
    active = BooleanField(default=True)


class FavoriteMovie(BaseModel):
    user_id = IntegerField()
    movie_id = IntegerField()
    search_time = CharField()
    genre_ids = CharField(default="")

    class Meta:
        table_name = "favorites"
        indexes = ((("user_id", "movie_id"), True),)


class FavoriteActor(BaseModel):
    user_id = IntegerField()
    actor_id = IntegerField()
    search_time = CharField()

    class Meta:
        table_name = "actor_favorites"
        indexes = ((("user_id", "actor_id"), True),)


class FavoriteDirector(BaseModel):
    user_id = IntegerField()
    director_id = IntegerField()
    search_time = CharField()

    class Meta:
        table_name = "director_favorites"
        indexes = ((("user_id", "director_id"), True),)


class BotConfig(BaseModel):
    param_name = CharField(unique=True)
    param_value = CharField()

    class Meta:
        table_name = "bot_config"


class MovieSearchLog(BaseModel):
    user_id = IntegerField()
    movie_id = IntegerField()
    search_time = CharField()
    genre_ids = CharField(default="")
    searched_from = CharField(default="movie")

    class Meta:
        table_name = "movie_search_log"


class ActorSearchLog(BaseModel):
    user_id = IntegerField()
    actor_id = IntegerField()
    search_time = CharField()
    searched_from = CharField(default="str")

    class Meta:
        table_name = "actor_search_log"


class DirectorSearchLog(BaseModel):
    user_id = IntegerField()
    director_id = IntegerField()
    search_time = CharField()
    searched_from = CharField(default="str")

    class Meta:
        table_name = "director_search_log"


class UserMessage(BaseModel):
    user_id = IntegerField()
    username = CharField(null=True)
    user_msg = CharField()
    created_at = CharField(default=now_str)

    class Meta:
        table_name = "msg_from_user"


class UserBlockLog(BaseModel):
    user_id = IntegerField()
    admin_id = IntegerField()
    action = CharField()
    created_at = CharField(default=now_str)

    class Meta:
        table_name = "user_block_log"
