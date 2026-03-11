from .models import db, User
import sqlite3
from database.db import DB_PATH
from database.bot_config import ensure_default_bot_config


def _table_exists(cur: sqlite3.Cursor, name: str) -> bool:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def _column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def init_db():
    db.connect(reuse_if_open=True)
    db.create_tables([User])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if _table_exists(cur, "user") and not _column_exists(cur, "user", "language"):
        try:
            cur.execute("ALTER TABLE user ADD COLUMN language TEXT DEFAULT 'en'")
        except sqlite3.OperationalError:
            pass

    if _table_exists(cur, "user") and not _column_exists(cur, "user", "active"):
        try:
            cur.execute("ALTER TABLE user ADD COLUMN active INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass

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

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS actor_favorites (
            user_id INTEGER NOT NULL,
            actor_id INTEGER NOT NULL,
            search_time TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS director_favorites (
            user_id INTEGER NOT NULL,
            director_id INTEGER NOT NULL,
            search_time TEXT NOT NULL
        )
        """
    )

    if _table_exists(cur, "search_log") and not _table_exists(cur, "movie_search_log"):
        try:
            cur.execute("ALTER TABLE search_log RENAME TO movie_search_log")
        except sqlite3.OperationalError:
            pass

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS movie_search_log (
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            search_time TEXT NOT NULL,
            genre_ids TEXT DEFAULT '',
            searched_from TEXT DEFAULT 'movie'
        )
        """
    )

    if not _column_exists(cur, "movie_search_log", "searched_from"):
        try:
            cur.execute(
                "ALTER TABLE movie_search_log ADD COLUMN searched_from TEXT DEFAULT 'movie'"
            )
        except sqlite3.OperationalError:
            pass

    cur.execute(
        """
        UPDATE movie_search_log
        SET searched_from = CASE searched_from
            WHEN 'str' THEN 'movie'
            WHEN 'straight' THEN 'movie'
            WHEN 'movie' THEN 'movie'
            WHEN 'fav' THEN 'actor'
            WHEN 'actor' THEN 'actor'
            WHEN 'dir' THEN 'director'
            WHEN 'director' THEN 'director'
            ELSE searched_from
        END
        """
    )

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
    if not _column_exists(cur, "actor_search_log", "searched_from"):
        try:
            cur.execute(
                "ALTER TABLE actor_search_log ADD COLUMN searched_from TEXT DEFAULT 'str'"
            )
        except sqlite3.OperationalError:
            pass

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
    if not _column_exists(cur, "director_search_log", "searched_from"):
        try:
            cur.execute(
                "ALTER TABLE director_search_log ADD COLUMN searched_from TEXT DEFAULT 'str'"
            )
        except sqlite3.OperationalError:
            pass

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS msg_from_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            user_msg TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    if _table_exists(cur, "msg_from_user") and not _column_exists(
        cur, "msg_from_user", "created_at"
    ):
        try:
            cur.execute(
                "ALTER TABLE msg_from_user ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            )
        except sqlite3.OperationalError:
            pass

    try:
        cur.execute(
            """
            UPDATE msg_from_user
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL OR TRIM(created_at) = ''
            """
        )
    except sqlite3.OperationalError:
        pass

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_block_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            admin_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()

    ensure_default_bot_config()
