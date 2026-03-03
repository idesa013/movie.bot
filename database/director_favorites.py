import sqlite3
from database.db import DB_PATH


def add_director_favorite(user_id: int, director_id: int, search_time: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO director_favorites (user_id, director_id, search_time)
        VALUES (?, ?, ?)
        """,
        (user_id, director_id, search_time),
    )
    conn.commit()
    conn.close()


def check_director_favorite(user_id: int, director_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM director_favorites WHERE user_id = ? AND director_id = ?",
        (user_id, director_id),
    )
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def remove_director_favorite(user_id: int, director_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM director_favorites WHERE user_id = ? AND director_id = ?",
        (user_id, director_id),
    )
    conn.commit()
    conn.close()
