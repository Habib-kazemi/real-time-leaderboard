from fastapi import HTTPException
from tasks.celery_app import app as celery_app
from shared.config.database import get_postgres_conn
from shared.config.permissions import Permission
from .model import LeaderboardModel
from .schema import LeaderboardResponse


async def get_leaderboard(game_id: str, user_permission: list, limit: int = 10) -> LeaderboardResponse:
    """Retrieve leaderboard for a game if user has permission."""
    if Permission.CAN_VIEW_LEADERBOARD.value not in user_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_view_leaderboard required")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT game_id, active, leaderboard_enabled FROM game WHERE game_id = %s", (game_id,))
            game = cur.fetchone()
            if not game:
                raise HTTPException(
                    status_code=400, detail="Game not found")
            if not game["leaderboard_enabled"]:
                raise HTTPException(
                    status_code=400, detail="Leaderboard disabled")
    finally:
        conn.close()

    entries = await LeaderboardModel.get_leaderboard(game_id, limit)
    return LeaderboardResponse(game_id=game_id, entries=entries)


async def get_score_report_by_country(game_id: str, user_permission: list) -> dict:
    """Retrieve total scores by country for a game if user has permission."""
    if Permission.CAN_VIEW_REPORT.value not in user_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_view_report required")

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT game_id FROM game WHERE game_id = %s", (game_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=400, detail="Game not found")
            cur.execute(
                """
                SELECT u.country, SUM(s.score) as total_score
                FROM score s
                JOIN users u ON s.user_id = u.user_id
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


async def get_active_users_report(start_time: str, end_time: str, user_permission: list) -> dict:
    """Retrieve active users count in a time range if user has permission."""
    if Permission.CAN_VIEW_REPORT.value not in user_permission:
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


async def generate_game_comparison_report(user_permission: list) -> str:
    """Generate async game comparison report and return task ID."""
    if Permission.CAN_VIEW_REPORT.value not in user_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_view_report required")
    task = celery_app.send_task("tasks.generate_game_comparison_report")
    return task.id


async def generate_team_performance_report(user_permission: list) -> str:
    """Generate async team performance report and return task ID."""
    if Permission.CAN_VIEW_REPORT.value not in user_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_view_report required")
    task = celery_app.send_task("tasks.generate_team_performance_report")
    return task.id


async def get_report_result(task_id: str, user_permission: list) -> dict:
    """Retrieve result of an async report by task ID."""
    if Permission.CAN_VIEW_REPORT.value not in user_permission:
        raise HTTPException(
            status_code=403, detail="Permission can_view_report required")
    result = celery_app.AsyncResult(task_id)
    if result.status == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    elif result.status == "SUCCESS":
        return {"task_id": task_id, "status": "success", "result": result.get()}
    else:
        raise HTTPException(
            status_code=400, detail=f"Task status: {result.status}")
