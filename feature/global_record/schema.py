from uuid import UUID
from pydantic import BaseModel, Field


class GlobalRecordResponse(BaseModel):
    """Schema for returning global record data."""
    game_id: str
    user_id: str
    username: str
    score: int
    timestamp: float
    session_id: UUID
