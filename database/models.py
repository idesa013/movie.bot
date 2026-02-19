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
