from database.models import BotConfig


DEFAULT_CONFIG = {
    "user_per_admin_page": "3",
    "qty_movie_fav": "30",
    "qty_actor_fav": "20",
    "qty_director_fav": "10",
}


def ensure_default_bot_config():
    for param_name, param_value in DEFAULT_CONFIG.items():
        BotConfig.get_or_create(
            param_name=param_name,
            defaults={"param_value": param_value},
        )


def get_config_value(param_name: str, default=None):
    row = BotConfig.get_or_none(BotConfig.param_name == param_name)
    if not row:
        return default
    return row.param_value


def get_config_int(param_name: str, default: int) -> int:
    value = get_config_value(param_name, str(default))
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
