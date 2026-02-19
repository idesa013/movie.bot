from .models import db, User


def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([User])
