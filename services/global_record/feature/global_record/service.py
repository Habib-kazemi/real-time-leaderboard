from datetime import datetime, timezone
from fastapi import HTTPException
import httpx
from shared.config.database import get_postgres_conn, get_redis_client
from .model import GlobalRecordModel


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

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://game-service:8001/v1/game/{game_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Game not found")

        response = await client.get(f"http://user-service:8000/v1/user/{user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="User not found")
        user = response.json()

    redis_client = get_redis_client()
    current_record = redis_client.hgetall(f"global_record:{game_id}")
    if not current_record or new_score > int(current_record.get("score", 0)):
        record_data = {
            "game_id": game_id,
            "user_id": user_id,
            "username": user["username"],
            "score": new_score,
            "timestamp": datetime.now(timezone.utc).timestamp() * 1000,
            "session_id": str(session_id)
        }
        await GlobalRecordModel.update_global_record(record_data)
        async with httpx.AsyncClient() as client:
            await client.publish("record_updates", f"global_record:{game_id}:{user_id}:{new_score}")
        return {"message": "Global record updated"}
    return {"message": "Score not high enough for global record"}
