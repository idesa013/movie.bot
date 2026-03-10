import sqlite3
from database.db import DB_PATH


def add_block_log(user_id: int, admin_id: int, action: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO user_block_log (user_id, admin_id, action)
        VALUES (?, ?, ?)
        """,
        (user_id, admin_id, action),
    )
    conn.commit()
    conn.close()


def get_last_block_time(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT created_at
        FROM user_block_log
        WHERE user_id = ? AND action = 'block'
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
