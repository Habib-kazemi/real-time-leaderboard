import json
from celery import Celery
from shared.config.database import get_redis_client, get_postgres_conn
from shared.config.settings import settings

app = Celery(
    'user_tasks',
    broker=f'amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//',
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
    include=['tasks']
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    broker_connection_retry_on_startup=True
)


@app.task(name="tasks.sync_scores_to_postgres")
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


@app.task(name="tasks.generate_game_comparison_report")
def generate_game_comparison_report():
    """Generate a report comparing game performance."""
    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT g.game_id, g.name, COUNT(s.user_id) as player_count, AVG(s.score) as avg_score
                FROM game g
                LEFT JOIN score s ON g.game_id = s.game_id
                GROUP BY g.game_id, g.name
                ORDER BY avg_score DESC
                """
            )
            report = [
                {"game_id": row["game_id"], "name": row["name"],
                    "player_count": row["player_count"], "avg_score": row["avg_score"]}
                for row in cur.fetchall()
            ]
    finally:
        conn.close()
    return {"report": report}


@app.task(name="tasks.generate_team_performance_report")
def generate_team_performance_report():
    """Generate a report on team performance."""
    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.username, u.type, COUNT(s.id) as score_count, SUM(s.score) as total_score
                FROM users u
                LEFT JOIN score s ON u.user_id = u.user_id
                WHERE u.type = 'team'
                GROUP BY u.user_id, u.username, u.type
                ORDER BY total_score DESC
                """
            )
            report = [
                {"username": row["username"], "type": row["type"],
                    "score_count": row["score_count"], "total_score": row["total_score"]}
                for row in cur.fetchall()
            ]
    finally:
        conn.close()
    return {"report": report}
