from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import httpx

from .schema import AdminUserUpdate, AdminGameUpdate
from .service import update_user_by_admin, update_game_by_admin

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://user-service:8000/v1/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://user-service:8000/v1/user/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return response.json()


@router.put("/user/{user_id}")
async def update_user_by_admin_endpoint(
    user_id: str,
    update_data: AdminUserUpdate,
    current_user: dict = Depends(get_current_user)
):
    return await update_user_by_admin(user_id, update_data, current_user)


@router.put("/game/{game_id}")
async def update_game_by_admin_endpoint(
    game_id: str,
    update_data: AdminGameUpdate,
    current_user: dict = Depends(get_current_user)
):
    return await update_game_by_admin(game_id, update_data, current_user)
