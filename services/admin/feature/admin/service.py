from fastapi import HTTPException
import httpx

from config.database import get_postgres_conn
from config.permissions import Permission
from feature.admin.model import AdminModel
from feature.admin.schema import AdminUserUpdate, AdminGameUpdate


async def update_user_by_admin(user: AdminUserUpdate, admin_permissions: list) -> dict:
    """Update user data if admin has permission."""
    if Permission.CAN_MANAGE_USER.value not in admin_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_manage_user required")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://user-service:8000/v1/user/{user.user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")

    user_data = user.model_dump(exclude_unset=True)
    await AdminModel.update_user(user_data)
    return {"message": "User updated successfully"}


async def update_game_by_admin(game: AdminGameUpdate, admin_permissions: list) -> dict:
    """Update game data if admin has permission."""
    if Permission.CAN_MANAGE_GAME.value not in admin_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_manage_game required")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://game-service:8001/v1/game/{game.game_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Game not found")

    game_data = game.model_dump(exclude_unset=True)
    await AdminModel.update_game(game_data)
    return {"message": "Game updated successfully"}
