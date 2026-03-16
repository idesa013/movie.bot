from database.models import UserMessage, now_str


def add_user_message(user_id: int, username: str | None, user_msg: str):
    UserMessage.create(
        user_id=user_id,
        username=username,
        user_msg=user_msg,
        created_at=now_str(),
    )


def get_all_user_messages(user_id: int):
    rows = (
        UserMessage.select()
        .where(UserMessage.user_id == user_id)
        .order_by(UserMessage.id.desc())
    )

    return [
        (row.id, row.user_id, row.username, row.user_msg, row.created_at)
        for row in rows
    ]


def get_user_messages_from_date(user_id: int, from_date: str | None):
    query = UserMessage.select().where(UserMessage.user_id == user_id)

    if from_date:
        query = query.where(UserMessage.created_at >= from_date)

    query = query.order_by(UserMessage.id.desc())

    return [
        (row.id, row.user_id, row.username, row.user_msg, row.created_at)
        for row in query
    ]
