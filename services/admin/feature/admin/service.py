from fastapi import HTTPException
from shared.config.permissions import Permission
from shared.config.database import get_postgres_conn
from .model import AdminModel
from .schema import AdminUserUpdate, AdminGameUpdate


async def update_user_by_admin(user_id: str, user: AdminUserUpdate, admin_permission: list) -> dict:
    """Update user data if admin has permission."""
    if Permission.CAN_MANAGE_USER.value not in admin_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_manage_user required")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="User not found")
    finally:
        conn.close()

    user_data = user.model_dump(exclude_unset=True)
    user_data["user_id"] = user_id
    await AdminModel.update_user(user_data)
    return {"message": "User updated successfully"}


async def update_game_by_admin(game_id: str, game: AdminGameUpdate, admin_permission: list) -> dict:
    """Update game data if admin has permission."""
    if Permission.CAN_MANAGE_GAME.value not in admin_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_manage_game required")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT game_id FROM game WHERE game_id = %s", (game_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Game not found")
    finally:
        conn.close()

    game_data = game.model_dump(exclude_unset=True)
    game_data["game_id"] = game_id
    await AdminModel.update_game(game_data)
    return {"message": "Game updated successfully"}
