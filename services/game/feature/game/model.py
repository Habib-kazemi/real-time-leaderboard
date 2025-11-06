from datetime import datetime
from shared.config.database import get_redis_client, get_postgres_conn


class GameModel:
    """Model for handling game data in Redis and PostgreSQL."""

    @staticmethod
    async def create_game(game_data: dict) -> str:
        """Create a new game in Redis and PostgreSQL."""
        game_id = game_data["game_id"]
        game_data["created_at"] = int(datetime.utcnow().timestamp() * 1000)
        game_data["updated_at"] = game_data["created_at"]
        game_data["play_count"] = 0

        # Redis: bool → int
        redis_data = game_data.copy()
        bool_fields = ["active", "leaderboard_enabled", "team_allowed"]
        for field in bool_fields:
            if field in redis_data:
                redis_data[field] = int(redis_data[field])

        # PostgreSQL: bool
        pg_data = game_data

        # Redis
        redis_client = get_redis_client()
        redis_client.hset(f"game:{game_id}", mapping=redis_data)

        # PostgreSQL
        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO game (game_id, name, description, category, active, max_score, min_score, play_count, created_at, updated_at, leaderboard_enabled, team_allowed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, to_timestamp(%s), to_timestamp(%s), %s, %s)
                    """,
                    (
                        game_id,
                        pg_data["name"],
                        pg_data["description"],
                        pg_data["category"],
                        pg_data["active"],
                        pg_data["max_score"],
                        pg_data["min_score"],
                        pg_data["play_count"],
                        pg_data["created_at"] / 1000,
                        pg_data["updated_at"] / 1000,
                        pg_data["leaderboard_enabled"],
                        pg_data["team_allowed"]
                    )
                )
            conn.commit()
        finally:
            conn.close()
        return game_id

    @staticmethod
    async def get_game(game_id: str) -> dict | None:
        """Retrieve game data from Redis or PostgreSQL."""
        redis_client = get_redis_client()
        game_data = redis_client.hgetall(f"game:{game_id}")
        if game_data:
            bool_fields = ["active", "leaderboard_enabled", "team_allowed"]
            for field in bool_fields:
                if field in game_data:
                    game_data[field] = bool(int(game_data[field]))
            return game_data

        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM game WHERE game_id = %s", (game_id,))
                game = cur.fetchone()
                if game:
                    game_data = dict(game)

                    redis_data = game_data.copy()
                    for field in ["active", "leaderboard_enabled", "team_allowed"]:
                        if field in redis_data:
                            redis_data[field] = int(redis_data[field])
                    redis_client.hset(f"game:{game_id}", mapping=redis_data)
                    return game_data
        finally:
            conn.close()
        return None
