import json
from datetime import datetime

from config.database import get_redis_client, get_postgres_conn


class ScoreModel:
    """Model for handling score data in Redis and PostgreSQL."""

    @staticmethod
    async def create_score(score_data: dict) -> int:
        """Create a new score in Redis and PostgreSQL."""
        score_data["timestamp"] = int(datetime.utcnow().timestamp() * 1000)
        score_data["is_record"] = False
        redis_client = get_redis_client()
        redis_client.lpush(
            f"score:{score_data['user_id']}:{score_data['game_id']}",
            json.dumps(score_data)
        )

        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO score (user_id, game_id, score, timestamp, session_id, is_record, device)
                    VALUES (%s, %s, %s, to_timestamp(%s), %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        score_data["user_id"],
                        score_data["game_id"],
                        score_data["score"],
                        score_data["timestamp"] / 1000,
                        score_data["session_id"],
                        score_data["is_record"],
                        score_data["device"]
                    )
                )
                score_id = cur.fetchone()["id"]
            conn.commit()
        finally:
            conn.close()
        return score_id
