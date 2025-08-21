from datetime import datetime

from config.database import get_redis_client, get_postgres_conn


class GameModel:
    """Model for handling game data in Redis and PostgreSQL."""

    @staticmethod
    async def create_game(game_data: dict) -> str:
        """Create a new game in Redis and PostgreSQL."""
        game_id = game_data["game_id"]
        game_data["created_at"] = int(datetime.utcnow().timestamp() * 1000)
        game_data["updated_at"] = game_data["created_at"]
        game_data["play_count"] = 0

        redis_client = get_redis_client()
        redis_client.hset(f"game:{game_id}", mapping=game_data)

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
                        game_data["name"],
                        game_data["description"],
                        game_data["category"],
                        game_data["active"],
                        game_data["max_score"],
                        game_data["min_score"],
                        game_data["play_count"],
                        game_data["created_at"] / 1000,
                        game_data["updated_at"] / 1000,
                        game_data["leaderboard_enabled"],
                        game_data["team_allowed"]
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
            return game_data

        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM game WHERE game_id = %s", (game_id,))
                game = cur.fetchone()
                if game:
                    game_data = dict(game)
                    redis_client.hset(f"game:{game_id}", mapping=game_data)
                    return game_data
        finally:
            conn.close()
        return None
