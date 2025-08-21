from fastapi import APIRouter, Depends, HTTPException

from config.permissions import Permission
from feature.game.schema import GameCreate, GameResponse
from feature.game.service import create_game
from feature.user.router import get_current_user
from feature.game.model import GameModel


router = APIRouter(prefix="/v1")


@router.post("/admin/game", response_model=GameResponse)
async def create_game_endpoint(game: GameCreate, user: dict = Depends(get_current_user)):
    """Create a new game endpoint."""
    result = await create_game(game, user["permission"])
    game_data = await GameModel.get_game(result["game_id"])
    return game_data
