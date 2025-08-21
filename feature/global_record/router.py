from fastapi import APIRouter, Depends

from feature.global_record.schema import GlobalRecordResponse
from feature.global_record.service import update_global_record
from feature.user.router import get_current_user


router = APIRouter(prefix="/v1")


@router.post("/global-record/{score_id}", response_model=GlobalRecordResponse)
async def update_global_record_endpoint(score_id: int, user: dict = Depends(get_current_user)):
    """Update global record for a score."""
    result = await update_global_record(score_id, user["user_id"], user["permission"])
    return result
