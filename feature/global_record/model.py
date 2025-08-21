from config.database import get_redis_client, get_postgres_conn


class GlobalRecordModel:
    """Model for handling global record data in Redis and PostgreSQL."""

    @staticmethod
    async def update_global_record(record_data: dict) -> None:
        """Update global record for a game."""
        redis_client = get_redis_client()
        redis_client.hset(
            f"global_record:{record_data['game_id']}", mapping=record_data)

        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO global_record (game_id, user_id, username, score, timestamp, session_id)
                    VALUES (%s, %s, %s, %s, to_timestamp(%s), %s)
                    ON CONFLICT (game_id) DO UPDATE
                    SET user_id = EXCLUDED.user_id,
                        username = EXCLUDED.username,
                        score = EXCLUDED.score,
                        timestamp = EXCLUDED.timestamp,
                        session_id = EXCLUDED.session_id
                    """,
                    (
                        record_data["game_id"],
                        record_data["user_id"],
                        record_data["username"],
                        record_data["score"],
                        record_data["timestamp"] / 1000,
                        record_data["session_id"]
                    )
                )
            conn.commit()
        finally:
            conn.close()
