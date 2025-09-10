from config.database import get_redis_client


class LeaderboardModel:
    """Model for handling leaderboard data in Redis."""

    @staticmethod
    async def get_leaderboard(game_id: str, limit: int = 10) -> list:
        """Retrieve top scores for a game from Redis."""
        redis_client = get_redis_client()
        leaderboard = redis_client.zrevrange(
            f"leaderboard:{game_id}", 0, limit - 1, withscores=True)
        result = []
        for rank, (user_id, score) in enumerate(leaderboard, 1):
            user_data = redis_client.hgetall(f"user:{user_id}")
            result.append({
                "user_id": user_id,
                "username": user_data.get("username", "Unknown"),
                "score": int(score),
                "rank": rank
            })
        return result
