import json
import uuid
from datetime import datetime

from config.database import get_redis_client, get_postgres_conn


class UserModel:
    """Model for handling user data in Redis and PostgreSQL."""

    @staticmethod
    async def create_user(user_data: dict) -> str:
        """Create a new user in Redis and PostgreSQL."""
        user_id = str(uuid.uuid4())
        user_data["user_id"] = user_id
        user_data["created_at"] = int(datetime.utcnow().timestamp() * 1000)
        user_data["permission"] = json.dumps(
            [perm.value for perm in user_data["permission"]])
        user_data["team_member"] = json.dumps(user_data["team_member"])

        # Store in Redis
        redis_client = get_redis_client()
        redis_client.hset(f"user:{user_id}", mapping=user_data)

        # Store in PostgreSQL
        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user (user_id, username, password, email, full_name, country, type, team_member, total_score, level, created_at, permission)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, to_timestamp(%s), %s)
                    """,
                    (
                        user_id,
                        user_data["username"],
                        user_data["password"],
                        user_data["email"],
                        user_data["full_name"],
                        user_data["country"],
                        user_data["type"],
                        user_data["team_member"],
                        user_data["total_score"],
                        user_data["level"],
                        user_data["created_at"] / 1000,
                        user_data["permission"]
                    )
                )
            conn.commit()
        finally:
            conn.close()
        return user_id

    @staticmethod
    async def get_user(user_id: str) -> dict | None:
        """Retrieve user data from Redis or PostgreSQL."""
        redis_client = get_redis_client()
        user_data = redis_client.hgetall(f"user:{user_id}")
        if user_data:
            user_data["permission"] = json.loads(user_data["permission"])
            user_data["team_member"] = json.loads(user_data["team_member"])
            return user_data

        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM user WHERE user_id = %s", (user_id,))
                user = cur.fetchone()
                if user:
                    user_data = dict(user)
                    user_data["permission"] = json.loads(
                        user_data["permission"])
                    user_data["team_member"] = json.loads(
                        user_data["team_member"])
                    redis_client.hset(f"user:{user_id}", mapping=user_data)
                    return user_data
        finally:
            conn.close()
        return None
