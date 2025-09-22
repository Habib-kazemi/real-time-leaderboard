from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import httpx

from .schema import GameCreate
from .service import create_game

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


@router.post("/game", response_model=dict)
async def create_game_endpoint(game: GameCreate, current_user: dict = Depends(get_current_user)):
    return await create_game(game, current_user)
