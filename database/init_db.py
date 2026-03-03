from .models import db, User
import sqlite3
from database.db import DB_PATH


def init_db():
    # Peewee-модели
    db.connect(reuse_if_open=True)
    db.create_tables([User])

    # SQLite таблицы (для логов/избранного) — совместимо с текущей схемой проекта
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Избранное фильмов
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            search_time TEXT NOT NULL,
            genre_ids TEXT DEFAULT ''
        )
        """
    )

    # Лог поиска/открытия фильмов (+ searched_from)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS search_log (
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            search_time TEXT NOT NULL,
            genre_ids TEXT DEFAULT '',
            searched_from TEXT DEFAULT 'str'
        )
        """
    )

    # Избранное актёров
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS actor_favorites (
            user_id INTEGER NOT NULL,
            actor_id INTEGER NOT NULL,
            search_time TEXT NOT NULL
        )
        """
    )

    # Избранное режиссёров
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS director_favorites (
            user_id INTEGER NOT NULL,
            director_id INTEGER NOT NULL,
            search_time TEXT NOT NULL
        )
        """
    )

    # Логи поиска актёров
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS actor_search_log (
            user_id INTEGER NOT NULL,
            actor_id INTEGER NOT NULL,
            search_time TEXT NOT NULL,
            searched_from TEXT DEFAULT 'str'
        )
        """
    )

    # Логи поиска режиссёров
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS director_search_log (
            user_id INTEGER NOT NULL,
            director_id INTEGER NOT NULL,
            search_time TEXT NOT NULL,
            searched_from TEXT DEFAULT 'str'
        )
        """
    )

    conn.commit()
    conn.close()
