from fastapi import HTTPException

from config.database import get_postgres_conn
from config.permissions import Permission
from feature.admin.model import AdminModel
from feature.admin.schema import AdminUserUpdate, AdminGameUpdate


async def update_user_by_admin(user: AdminUserUpdate, admin_permissions: list) -> dict:
    """Update user data if admin has permission."""
    if Permission.CAN_MANAGE_USER.value not in admin_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_manage_user required")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM user WHERE user_id = %s",
                        (str(user.user_id),))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found")
    finally:
        conn.close()

    user_data = user.model_dump(exclude_unset=True)
    await AdminModel.update_user(user_data)
    return {"message": "User updated successfully"}


async def update_game_by_admin(game: AdminGameUpdate, admin_permissions: list) -> dict:
    """Update game data if admin has permission."""
    if Permission.CAN_MANAGE_GAME.value not in admin_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_manage_game required")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT game_id FROM game WHERE game_id = %s", (game.game_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Game not found")
    finally:
        conn.close()

    game_data = game.model_dump(exclude_unset=True)
    await AdminModel.update_game(game_data)
    return {"message": "Game updated successfully"}
