from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ScoreCreate(BaseModel):
    """Schema for submitting a new score."""
    game_id: str = Field(..., max_length=50, description="Game identifier")
    score: int = Field(..., ge=0, description="Score value")
    session_id: UUID = Field(..., description="Unique session identifier")
    device: Optional[str] = Field(
        None, max_length=50, description="Device type")


class ScoreResponse(BaseModel):
    """Schema for returning score data."""
    user_id: str
    game_id: str
    score: int
    timestamp: float
    session_id: UUID
    is_record: bool
    device: Optional[str]
