from fastapi import APIRouter, Depends

from feature.leaderboard.schema import LeaderboardResponse
from feature.leaderboard.service import get_leaderboard, get_score_report_by_country, get_active_users_report
from feature.user.router import get_current_user


router = APIRouter(prefix="/v1")


@router.get("/leaderboard/{game_id}", response_model=LeaderboardResponse)
async def get_leaderboard_endpoint(game_id: str, user: dict = Depends(get_current_user)):
    """Retrieve leaderboard for a game."""
    return await get_leaderboard(game_id, user["permission"])


@router.get("/report/score-by-country/{game_id}", response_model=dict)
async def get_score_report_by_country_endpoint(game_id: str, user: dict = Depends(get_current_user)):
    """Retrieve score report by country for a game."""
    return await get_score_report_by_country(game_id, user["permission"])


@router.get("/report/active-users", response_model=dict)
async def get_active_users_report_endpoint(start_time: str, end_time: str, user: dict = Depends(get_current_user)):
    """Retrieve active users report for a time range."""
    return await get_active_users_report(start_time, end_time, user["permission"])
