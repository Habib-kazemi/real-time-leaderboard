from fastapi import APIRouter, Depends

from feature.admin.schema import AdminUserUpdate, AdminGameUpdate
from feature.admin.service import update_user_by_admin, update_game_by_admin
from feature.user.router import get_current_user


router = APIRouter(prefix="/v1/admin")


@router.put("/user", response_model=dict)
async def update_user_endpoint(user: AdminUserUpdate, admin: dict = Depends(get_current_user)):
    """Update user data by admin."""
    return await update_user_by_admin(user, admin["permission"])


@router.put("/game", response_model=dict)
async def update_game_endpoint(game: AdminGameUpdate, admin: dict = Depends(get_current_user)):
    """Update game data by admin."""
    return await update_game_by_admin(game, admin["permission"])
