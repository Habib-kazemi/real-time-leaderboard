import json
from celery import Celery
from config.database import get_redis_client, get_postgres_conn
from config.settings import settings


app = Celery(
    "leaderboard",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)


app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True
)


@app.task
def sync_scores_to_postgres():
    """Sync scores from Redis to PostgreSQL."""
    redis_client = get_redis_client()
    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            keys = redis_client.keys("score:*")
            for key in keys:
                scores = redis_client.lrange(key, 0, -1)
                for score_data in scores:
                    data = json.loads(score_data)
                    cur.execute(
                        """
                        INSERT INTO score (user_id, game_id, score, timestamp, session_id, is_record, device)
                        VALUES (%s, %s, %s, to_timestamp(%s), %s, %s, %s)
                        ON CONFLICT (session_id) DO NOTHING
                        """,
                        (
                            data["user_id"],
                            data["game_id"],
                            data["score"],
                            data["timestamp"] / 1000,
                            data["session_id"],
                            data["is_record"],
                            data["device"]
                        )
                    )
            conn.commit()
            for key in keys:
                redis_client.delete(key)
    finally:
        conn.close()
