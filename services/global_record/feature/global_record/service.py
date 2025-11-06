from datetime import datetime, timezone
from fastapi import HTTPException
import pika
from shared.config.permissions import Permission
from shared.config.database import get_postgres_conn, get_redis_client
from shared.config.settings import settings
from .model import GlobalRecordModel


async def update_global_record(score_id: int, user_id: str, user_permission: list) -> dict:
    """Update global record if score is higher."""
    if Permission.CAN_SUBMIT_SCORE.value not in user_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_submit_score required"
        )

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT game_id, score, session_id, user_id FROM score WHERE id = %s", (
                    score_id,)
            )
            score = cur.fetchone()
            if not score:
                raise HTTPException(status_code=400, detail="Score not found")

            game_id, new_score, session_id, score_user_id = (
                score["game_id"], score["score"], score["session_id"], score["user_id"]
            )

            if score_user_id != user_id:
                raise HTTPException(
                    status_code=403, detail="User not authorized to update this score"
                )

            cur.execute("SELECT 1 FROM game WHERE game_id = %s", (game_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=400, detail="Game not found")

            cur.execute(
                "SELECT username FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=400, detail="User not found")

    finally:
        conn.close()

    redis_client = get_redis_client()
    current_record = redis_client.hgetall(f"global_record:{game_id}")
    current_score = int(current_record.get(
        "score", 0)) if current_record else 0

    if new_score > current_score:
        record_data = {
            "game_id": game_id,
            "user_id": user_id,
            "username": user["username"],
            "score": new_score,
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
            "session_id": str(session_id)
        }

        await GlobalRecordModel.update_global_record(record_data)

        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    credentials=pika.PlainCredentials(
                        settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD
                    ),
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue="record_updates", durable=True)
            channel.basic_publish(
                exchange="",
                routing_key="record_updates",
                body=f"global_record:{game_id}:{user_id}:{new_score}",
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
        except Exception as e:
            print(f"[WARN] RabbitMQ publish failed: {e}")

        return {"message": "Global record updated"}

    return {"message": "Score not high enough for global record"}
