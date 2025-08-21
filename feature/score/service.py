from fastapi import HTTPException
from config.database import get_postgres_conn
from config.permissions import Permission
from feature.game.model import GameModel
from feature.score.model import ScoreModel
from feature.score.schema import ScoreCreate


async def submit_score(score: ScoreCreate, user_id: str, user_permissions: list) -> dict:
    """Submit a new score if user has permission."""
    if Permission.CAN_SUBMIT_SCORE.value not in user_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_submit_score required")

    game = await GameModel.get_game(score.game_id)
    if not game or not game["active"]:
        raise HTTPException(
            status_code=400, detail="Game not found or inactive")

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

    score_data = score.dict()
    score_data["user_id"] = user_id
    score_id = await ScoreModel.create_score(score_data)
    return {"score_id": score_id, "message": "Score submitted successfully"}
