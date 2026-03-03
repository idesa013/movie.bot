import sqlite3
from database.db import DB_PATH


def add_actor_favorite(user_id: int, actor_id: int, search_time: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO actor_favorites (user_id, actor_id, search_time)
        VALUES (?, ?, ?)
        """,
        (user_id, actor_id, search_time),
    )
    conn.commit()
    conn.close()


def check_actor_favorite(user_id: int, actor_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM actor_favorites WHERE user_id = ? AND actor_id = ?",
        (user_id, actor_id),
    )
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def remove_actor_favorite(user_id: int, actor_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM actor_favorites WHERE user_id = ? AND actor_id = ?",
        (user_id, actor_id),
    )
    conn.commit()
    conn.close()
