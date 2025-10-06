import json
import uuid
from datetime import datetime, timezone
from shared.config.database import get_redis_client, get_postgres_conn


class UserModel:
    """Model for handling user data in Redis and PostgreSQL."""

    @staticmethod
    async def create_user(user_data: dict) -> str:
        """Create a new user in Redis and PostgreSQL."""
        user_id = str(uuid.uuid4())
        user_data["user_id"] = user_id
        user_data["created_at"] = int(
            datetime.now(timezone.utc).timestamp() * 1000)
        user_data["permission"] = json.dumps(
            user_data.get("permission", ["can_submit_score", "can_view_leaderboard"]))
        user_data["team_member"] = json.dumps(user_data.get("team_member", []))

        # Store in Redis
        redis_client = get_redis_client()
        redis_client.hset(f"user:{user_id}", mapping=user_data)

        # Store in PostgreSQL
        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (user_id, username, password, email, full_name, country, type, team_member, total_score, level, created_at, permission)
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
                    "SELECT user_id, username, password, email, full_name, country, type, team_member, total_score, level, created_at, permission FROM users WHERE user_id = %s", (user_id,))
                user = cur.fetchone()
                if user:
                    user_data = {
                        "user_id": user["user_id"],
                        "username": user["username"],
                        "password": user["password"],
                        "email": user["email"],
                        "full_name": user["full_name"],
                        "country": user["country"],
                        "type": user["type"],
                        "team_member": json.loads(user["team_member"]),
                        "total_score": user["total_score"],
                        "level": user["level"],
                        "created_at": int(user["created_at"].timestamp() * 1000),
                        "permission": json.loads(user["permission"])
                    }
                    redis_client.hset(f"user:{user_id}", mapping=user_data)
                    return user_data
        finally:
            conn.close()
        return None
