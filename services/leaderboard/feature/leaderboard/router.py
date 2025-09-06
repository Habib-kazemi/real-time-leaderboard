from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import httpx

from .schema import LeaderboardResponse
from .service import (
    get_leaderboard,
    get_score_report_by_country,
    get_active_users_report,
    generate_game_comparison_report,
    generate_team_performance_report,
    get_report_result
)

router = APIRouter(prefix="/v1")
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


@router.get("/leaderboard/{game_id}", response_model=LeaderboardResponse)
async def get_leaderboard_endpoint(game_id: str, limit: int = 10, current_user: dict = Depends(get_current_user)):
    return await get_leaderboard(game_id, current_user["permission"], limit)


@router.get("/report/country/{game_id}")
async def get_score_report_by_country_endpoint(game_id: str, current_user: dict = Depends(get_current_user)):
    return await get_score_report_by_country(game_id, current_user["permission"])


@router.get("/report/active-users")
async def get_active_users_report_endpoint(start_time: str, end_time: str, current_user: dict = Depends(get_current_user)):
    return await get_active_users_report(start_time, end_time, current_user["permission"])


@router.post("/report/game-comparison")
async def generate_game_comparison_report_endpoint(current_user: dict = Depends(get_current_user)):
    return await generate_game_comparison_report(current_user["permission"])


@router.post("/report/team-performance")
async def generate_team_performance_report_endpoint(current_user: dict = Depends(get_current_user)):
    return await generate_team_performance_report(current_user["permission"])


@router.get("/report/result/{task_id}")
async def get_report_result_endpoint(task_id: str, current_user: dict = Depends(get_current_user)):
    return await get_report_result(task_id, current_user["permission"])
