from datetime import datetime
from fastapi import APIRouter, Depends
from services.user.feature.user.router import get_current_user
from .schema import ScoreCreate, ScoreResponse
from .service import submit_score


router = APIRouter(prefix="/v1")


@router.post("/score", response_model=ScoreResponse)
async def submit_score_endpoint(score: ScoreCreate, user: dict = Depends(get_current_user)):
    """Submit a new score endpoint."""
    await submit_score(score, user["user_id"], user["permission"])
    return {**score.dict(), "user_id": user["user_id"], "timestamp": datetime.utcnow().timestamp(), "is_record": False}
