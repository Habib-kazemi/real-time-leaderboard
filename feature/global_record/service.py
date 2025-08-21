from datetime import datetime
from fastapi import HTTPException
from config.database import get_postgres_conn, get_redis_client
from feature.game.model import GameModel
from feature.global_record.model import GlobalRecordModel
from feature.user.model import UserModel


async def update_global_record(score_id: int, user_id: str) -> dict:
    """Update global record if score is higher."""
    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT game_id, score, session_id FROM score WHERE id = %s", (score_id,))
            score = cur.fetchone()
            if not score:
                raise HTTPException(status_code=400, detail="Score not found")
            game_id, new_score, session_id = score["game_id"], score["score"], score["session_id"]
    finally:
        conn.close()

    game = await GameModel.get_game(game_id)
    if not game:
        raise HTTPException(status_code=400, detail="Game not found")

    redis_client = get_redis_client()
    current_record = redis_client.hgetall(f"global_record:{game_id}")
    if not current_record or new_score > int(current_record.get("score", 0)):
        user = await UserModel.get_user(user_id)
        record_data = {
            "game_id": game_id,
            "user_id": user_id,
            "username": user["username"],
            "score": new_score,
            "timestamp": datetime.utcnow().timestamp() * 1000,
            "session_id": str(session_id)
        }
        await GlobalRecordModel.update_global_record(record_data)
        return {"message": "Global record updated"}
    return {"message": "Score not high enough for global record"}
