from fastapi import HTTPException
import httpx
from shared.config.database import get_postgres_conn
from shared.config.permissions import Permission
from .model import ScoreModel
from .schema import ScoreCreate


async def submit_score(score: ScoreCreate, user_id: str, user_permissions: list) -> dict:
    """Submit a new score if user has permission."""
    if Permission.CAN_SUBMIT_SCORE.value not in user_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_submit_score required")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://game-service:8001/v1/game/{score.game_id}")
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Game not found or inactive")
        game = response.json()
        if not game["active"]:
            raise HTTPException(status_code=400, detail="Game is inactive")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT session_id FROM score WHERE session_id = %s", (str(score.session_id),))
            if cur.fetchone():
                raise HTTPException(
                    status_code=400, detail="Session ID already exists")
    finally:
        conn.close()

    score_data = score.model_dump()
    score_data["user_id"] = user_id
    score_id = await ScoreModel.create_score(score_data)

    async with httpx.AsyncClient() as client:
        await client.publish("score_updates", f"score:{score_id}:{user_id}:{score.game_id}")
    return {"score_id": score_id, "message": "Score submitted successfully"}
