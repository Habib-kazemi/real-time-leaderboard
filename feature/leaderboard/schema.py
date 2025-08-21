from typing import List
from pydantic import BaseModel, Field


class LeaderboardEntry(BaseModel):
    """Schema for a single leaderboard entry."""
    user_id: str
    username: str
    score: int
    rank: int


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard data."""
    game_id: str
    entries: List[LeaderboardEntry] = Field(...,
                                            description="List of leaderboard entries")
