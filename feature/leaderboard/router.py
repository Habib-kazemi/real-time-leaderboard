from fastapi import APIRouter, Depends

from feature.leaderboard.schema import LeaderboardResponse
from feature.leaderboard.service import get_leaderboard
from feature.user.router import get_current_user


router = APIRouter(prefix="/v1")


@router.get("/leaderboard/{game_id}", response_model=LeaderboardResponse)
async def get_leaderboard_endpoint(game_id: str, user: dict = Depends(get_current_user)):
    """Retrieve leaderboard for a game."""
    return await get_leaderboard(game_id, user["permission"])
