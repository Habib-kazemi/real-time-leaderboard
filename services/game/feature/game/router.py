from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from shared.config.settings import settings
from .schema import GameCreate
from .service import create_game

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/v1/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        permission = payload.get("permission", [])
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "permission": permission}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/game", response_model=dict)
async def create_game_endpoint(game: GameCreate, current_user: dict = Depends(get_current_user)):
    return await create_game(game, current_user["permission"])
