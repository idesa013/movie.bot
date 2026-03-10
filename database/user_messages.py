import sqlite3
from database.db import DB_PATH


def add_user_message(user_id: int, username: str | None, user_msg: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO msg_from_user (user_id, username, user_msg, created_at)
        VALUES (?, ?, ?, datetime('now', 'localtime'))
        """,
        (user_id, username, user_msg),
    )
    conn.commit()
    conn.close()


def get_all_user_messages(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, user_id, username, user_msg, created_at
        FROM msg_from_user
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_user_messages_from_date(user_id: int, from_date: str | None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if from_date:
        cur.execute(
            """
            SELECT id, user_id, username, user_msg, created_at
            FROM msg_from_user
            WHERE user_id = ?
              AND created_at >= ?
            ORDER BY id DESC
            """,
            (user_id, from_date),
        )
    else:
        cur.execute(
            """
            SELECT id, user_id, username, user_msg, created_at
            FROM msg_from_user
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        )

    rows = cur.fetchall()
    conn.close()
    return rows
