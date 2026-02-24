import sqlite3
from datetime import datetime
from database.db import DB_PATH


def log_movie_search(
    user_id: int, movie_id: int, search_time: str, genre_ids: str = ""
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO search_log (user_id, movie_id, search_time, genre_ids)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, movie_id, search_time, genre_ids),
    )

    conn.commit()
    conn.close()
