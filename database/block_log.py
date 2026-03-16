from database.models import UserBlockLog


def add_block_log(user_id: int, admin_id: int, action: str):
    UserBlockLog.create(
        user_id=user_id,
        admin_id=admin_id,
        action=action,
    )


def get_last_block_time(user_id: int):
    row = (
        UserBlockLog.select()
        .where((UserBlockLog.user_id == user_id) & (UserBlockLog.action == "block"))
        .order_by(UserBlockLog.id.desc())
        .first()
    )
    return row.created_at if row else None
