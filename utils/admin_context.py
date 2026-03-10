ADMIN_SELECTED = {}


def set_selected_user(admin_id: int, selected_user_id: int | None, page: int | None = None):
    if selected_user_id is None:
        ADMIN_SELECTED.pop(admin_id, None)
        return
    payload = {"selected_user_id": selected_user_id}
    if page is not None:
        payload["page"] = page
    else:
        old = ADMIN_SELECTED.get(admin_id) or {}
        payload["page"] = old.get("page", 1)
    ADMIN_SELECTED[admin_id] = payload


def get_selected_user(admin_id: int) -> int | None:
    payload = ADMIN_SELECTED.get(admin_id) or {}
    return payload.get("selected_user_id")


def get_selected_page(admin_id: int) -> int:
    payload = ADMIN_SELECTED.get(admin_id) or {}
    return int(payload.get("page", 1))


def has_selected_user(admin_id: int) -> bool:
    return get_selected_user(admin_id) is not None


def resolve_effective_user_id(current_user_id: int) -> int:
    return get_selected_user(current_user_id) or current_user_id
