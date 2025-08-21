from typing import Optional
from pydantic import BaseModel, Field


class GameCreate(BaseModel):
    """Schema for creating a new game."""
    game_id: str = Field(..., max_length=50,
                         description="Unique game identifier")
    name: str = Field(..., max_length=100, description="Game name")
    description: Optional[str] = Field(
        None, max_length=500, description="Game description")
    category: Optional[str] = Field(
        None, max_length=50, description="Game category")
    active: bool = Field(True, description="Game active status")
    max_score: Optional[int] = Field(
        None, description="Maximum score for the game")
    min_score: int = Field(0, description="Minimum score for the game")
    leaderboard_enabled: bool = Field(
        True, description="Enable leaderboard for the game")
    team_allowed: bool = Field(True, description="Allow team participation")


class GameResponse(BaseModel):
    """Schema for returning game data."""
    game_id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    active: bool
    max_score: Optional[int]
    min_score: int
    play_count: int
    created_at: float
    updated_at: float
    leaderboard_enabled: bool
    team_allowed: bool
