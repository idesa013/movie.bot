from peewee import Model


def add_favorite_record(
    model: type[Model], defaults: dict | None = None, **filters
) -> None:
    model.get_or_create(
        **filters,
        defaults=defaults or {},
    )


def check_favorite_record(model: type[Model], **filters) -> bool:
    query = model.select()
    for field_name, value in filters.items():
        query = query.where(getattr(model, field_name) == value)
    return query.exists()


def remove_favorite_record(model: type[Model], **filters) -> None:
    query = model.delete()
    for field_name, value in filters.items():
        query = query.where(getattr(model, field_name) == value)
    query.execute()
