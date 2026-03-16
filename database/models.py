from peewee import *
from datetime import datetime
from database.db import DB_PATH

db = SqliteDatabase(DB_PATH)


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
