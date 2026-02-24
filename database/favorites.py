import sqlite3
from database.db import DB_PATH


def add_favorite(
    user_id: int, movie_id: int, search_time: str, genre_ids: str = ""
) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO favorites (user_id, movie_id, search_time, genre_ids)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, movie_id, search_time, genre_ids),
    )

    conn.commit()
    conn.close()


def check_favorite(user_id: int, movie_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*) FROM favorites WHERE user_id = ? AND movie_id = ?
        """,
        (user_id, movie_id),
    )

    count = cur.fetchone()[0]
    conn.close()
    return count > 0


# Функция удаления фильма из избранного
def remove_favorite(user_id: int, movie_id: int) -> None:
    import sqlite3
    from database.db import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM favorites WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)
    )
    conn.commit()
    conn.close()
