import sqlite3
from database.db import DB_PATH


DEFAULT_CONFIG = {
    "user_per_admin_page": "3",
    "qty_movie_fav": "30",
    "qty_actor_fav": "20",
    "qty_director_fav": "10",
}


def ensure_default_bot_config():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bot_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            param_name TEXT NOT NULL UNIQUE,
            param_value TEXT NOT NULL
        )
        """
    )

    for param_name, param_value in DEFAULT_CONFIG.items():
        cur.execute(
            """
            INSERT OR IGNORE INTO bot_config (param_name, param_value)
            VALUES (?, ?)
            """,
            (param_name, param_value),
        )

    conn.commit()
    conn.close()


def get_config_value(param_name: str, default=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT param_value
        FROM bot_config
        WHERE param_name = ?
        LIMIT 1
        """,
        (param_name,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return default
    return row[0]


def get_config_int(param_name: str, default: int) -> int:
    value = get_config_value(param_name, str(default))
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
