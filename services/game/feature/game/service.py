from fastapi import HTTPException
from shared.config.database import get_postgres_conn
from shared.config.permissions import Permission
from .model import GameModel
from .schema import GameCreate


async def create_game(game: GameCreate, user_permission: list) -> dict:
    """Create a new game if user has permission."""
    if Permission.CAN_MANAGE_GAME.value not in user_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_manage_game required")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT game_id FROM game WHERE game_id = %s", (game.game_id,))
            if cur.fetchone():
                raise HTTPException(
                    status_code=400, detail="Game ID already exists")
    finally:
        conn.close()

    game_data = game.model_dump()
    game_id = await GameModel.create_game(game_data)
    return {"game_id": game_id, "message": "Game created successfully"}
