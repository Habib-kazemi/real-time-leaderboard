from fastapi import HTTPException
from config.permissions import Permission
from feature.game.model import GameModel
from feature.leaderboard.model import LeaderboardModel
from feature.leaderboard.schema import LeaderboardResponse


async def get_leaderboard(game_id: str, user_permissions: list, limit: int = 10) -> LeaderboardResponse:
    """Retrieve leaderboard for a game if user has permission."""
    if Permission.CAN_VIEW_LEADERBOARD.value not in user_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_view_leaderboard required")

    game = await GameModel.get_game(game_id)
    if not game or not game["leaderboard_enabled"]:
        raise HTTPException(
            status_code=400, detail="Game not found or leaderboard disabled")

    entries = await LeaderboardModel.get_leaderboard(game_id, limit)
    return LeaderboardResponse(game_id=game_id, entries=entries)
