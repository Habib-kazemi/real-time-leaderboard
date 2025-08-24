from fastapi import HTTPException

from config.database import get_postgres_conn
from config.permissions import Permission
from feature.game.model import GameModel
from feature.leaderboard.model import LeaderboardModel
from feature.leaderboard.schema import LeaderboardResponse


async def get_leaderboard(game_id: str, user_permissions: list, limit: int = 10) -> LeaderboardResponse:
    """Retrieve leaderboard for a game if user has permission."""
    if Permission.CAN_VIEW_LEADERBOARD.value not in user_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_view_leaderboard required")

    game = await GameModel.get_game(game_id)
    if not game or not game["leaderboard_enabled"]:
        raise HTTPException(
            status_code=400, detail="Game not found or leaderboard disabled")

    entries = await LeaderboardModel.get_leaderboard(game_id, limit)
    return LeaderboardResponse(game_id=game_id, entries=entries)


async def get_score_report_by_country(game_id: str, user_permissions: list) -> dict:
    """Retrieve total scores by country for a game if user has permission."""
    if Permission.CAN_VIEW_REPORT.value not in user_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_view_report required")

    game = await GameModel.get_game(game_id)
    if not game:
        raise HTTPException(status_code=400, detail="Game not found")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.country, SUM(s.score) as total_score
                FROM score s
                JOIN user u ON s.user_id = u.user_id
                WHERE s.game_id = %s
                GROUP BY u.country
                ORDER BY total_score DESC
                """,
                (game_id,)
            )
            report = [{"country": row["country"], "total_score": row["total_score"]}
                      for row in cur.fetchall()]
    finally:
        conn.close()
    return {"game_id": game_id, "report": report}


async def get_active_users_report(start_time: str, end_time: str, user_permissions: list) -> dict:
    """Retrieve active users count in a time range if user has permission."""
    if Permission.CAN_VIEW_REPORT.value not in user_permissions:
        raise HTTPException(
            status_code=403, detail="Permission can_view_report required")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(DISTINCT s.user_id) as active_users
                FROM score s
                WHERE s.timestamp BETWEEN %s AND %s
                """,
                (start_time, end_time)
            )
            result = cur.fetchone()
    finally:
        conn.close()
    return {"start_time": start_time, "end_time": end_time, "active_users": result["active_users"]}
