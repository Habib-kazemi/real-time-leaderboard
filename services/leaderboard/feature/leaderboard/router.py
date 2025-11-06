import json
from fastapi import APIRouter, WebSocket, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from shared.config.database import get_redis_client
from shared.config.settings import settings
from .schema import LeaderboardResponse
from .service import (
    get_leaderboard,
    get_score_report_by_country,
    get_active_users_report,
    generate_game_comparison_report,
    generate_team_performance_report,
    get_report_result
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/v1/login")


@router.websocket("/ws/leaderboard/{game_id}")
async def websocket_leaderboard(websocket: WebSocket, game_id: str):
    await websocket.accept()
    redis = await get_redis_client()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"leaderboard:{game_id}")
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                await websocket.send_text(json.dumps(message["data"]))
    except Exception:
        await websocket.close()
    finally:
        await pubsub.unsubscribe(f"leaderboard:{game_id}")
        await redis.close()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        permission = payload.get("permission", [])
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "permission": permission}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/leaderboard/{game_id}", response_model=LeaderboardResponse)
async def get_leaderboard_endpoint(
    game_id: str,
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    return await get_leaderboard(game_id, current_user["permission"], limit)


@router.get("/report/country/{game_id}")
async def get_score_report_by_country_endpoint(
    game_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await get_score_report_by_country(game_id, current_user["permission"])


@router.get("/report/active-users")
async def get_active_users_report_endpoint(
    start_time: str = Query(...,
                            description="ISO format, e.g. 2025-01-01T00:00:00Z"),
    end_time: str = Query(...,
                          description="ISO format, e.g. 2025-01-31T23:59:59Z"),
    current_user: dict = Depends(get_current_user)
):
    return await get_active_users_report(start_time, end_time, current_user["permission"])


@router.post("/report/game-comparison")
async def generate_game_comparison_report_endpoint(
    current_user: dict = Depends(get_current_user)
):
    return await generate_game_comparison_report(current_user["permission"])


@router.post("/report/team-performance")
async def generate_team_performance_report_endpoint(
    current_user: dict = Depends(get_current_user)
):
    return await generate_team_performance_report(current_user["permission"])


@router.get("/report/result/{task_id}")
async def get_report_result_endpoint(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await get_report_result(task_id, current_user["permission"])
