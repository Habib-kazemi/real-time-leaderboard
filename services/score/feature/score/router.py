from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import httpx

from .schema import ScoreCreate, ScoreResponse
from .service import submit_score

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


@router.post("/score", response_model=ScoreResponse)
async def submit_score_endpoint(score: ScoreCreate, current_user: dict = Depends(get_current_user)):
    return await submit_score(score, current_user)
