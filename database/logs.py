import sqlite3
from database.db import DB_PATH


def _has_column(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def log_movie_search(
    user_id: int,
    movie_id: int,
    search_time: str,
    genre_ids: str = "",
    searched_from: str = "str",
) -> None:
    """Логируем просмотр/поиск фильма.

    searched_from: 'str' | 'fav' | 'dir'
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Совместимость: если колонка searched_from ещё не добавлена - пишем по старой схеме
    if _has_column(cur, "search_log", "searched_from"):
        cur.execute(
            """
            INSERT INTO search_log (user_id, movie_id, search_time, genre_ids, searched_from)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, movie_id, search_time, genre_ids, searched_from),
        )
    else:
        cur.execute(
            """
            INSERT INTO search_log (user_id, movie_id, search_time, genre_ids)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, movie_id, search_time, genre_ids),
        )

    conn.commit()
    conn.close()


def log_actor_search(
    user_id: int,
    actor_id: int,
    search_time: str,
    searched_from: str = "str",
) -> None:
    """Логируем поиск/открытие карточки актёра.

    searched_from: обычно 'str' (поиск) или 'mov' (из карточки фильма)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if _has_column(cur, "actor_search_log", "searched_from"):
        cur.execute(
            """
            INSERT INTO actor_search_log (user_id, actor_id, search_time, searched_from)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, actor_id, search_time, searched_from),
        )
    else:
        cur.execute(
            """
            INSERT INTO actor_search_log (user_id, actor_id, search_time)
            VALUES (?, ?, ?)
            """,
            (user_id, actor_id, search_time),
        )

    conn.commit()
    conn.close()


def log_director_search(
    user_id: int,
    director_id: int,
    search_time: str,
    searched_from: str = "str",
) -> None:
    """Логируем поиск/открытие карточки режиссёра.

    searched_from: обычно 'str' (поиск) или 'mov' (из карточки фильма)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if _has_column(cur, "director_search_log", "searched_from"):
        cur.execute(
            """
            INSERT INTO director_search_log (user_id, director_id, search_time, searched_from)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, director_id, search_time, searched_from),
        )
    else:
        cur.execute(
            """
            INSERT INTO director_search_log (user_id, director_id, search_time)
            VALUES (?, ?, ?)
            """,
            (user_id, director_id, search_time),
        )

    conn.commit()
    conn.close()
