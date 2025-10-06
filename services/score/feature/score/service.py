from fastapi import HTTPException
import pika
from shared.config.database import get_postgres_conn
from shared.config.permissions import Permission
from shared.config.settings import settings
from .model import ScoreModel
from .schema import ScoreCreate


async def submit_score(score: ScoreCreate, user_id: str, user_permission: list) -> dict:
    """Submit a new score if user has permission."""
    if Permission.CAN_SUBMIT_SCORE.value not in user_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_submit_score required")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT game_id, active, leaderboard_enabled FROM game WHERE game_id = %s", (score.game_id,))
            game = cur.fetchone()
            if not game:
                raise HTTPException(
                    status_code=400, detail="Game not found")
            if not game["active"]:
                raise HTTPException(status_code=400, detail="Game is inactive")
    finally:
        conn.close()

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

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="score_updates")
    channel.basic_publish(
        exchange="", routing_key="score_updates",
        body=f"score:{score_id}:{user_id}:{score.game_id}"
    )
    connection.close()

    return {"score_id": score_id, "message": "Score submitted successfully"}
