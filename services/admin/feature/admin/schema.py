from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AdminUserUpdate(BaseModel):
    """Schema for updating user data by admin."""
    user_id: UUID = Field(..., description="User ID to update")
    username: Optional[str] = Field(
        None, max_length=50, description="New username")
    email: Optional[str] = Field(None, max_length=255, description="New email")
    full_name: Optional[str] = Field(
        None, max_length=100, description="New full name")
    country: Optional[str] = Field(
        None, max_length=2, description="ISO 3166-1 alpha-2 country code")
    permission: Optional[List[str]] = Field(
        None, description="List of user permissions")


class AdminGameUpdate(BaseModel):
    """Schema for updating game data by admin."""
    game_id: str = Field(..., max_length=50, description="Game ID to update")
    name: Optional[str] = Field(
        None, max_length=100, description="New game name")
    description: Optional[str] = Field(
        None, max_length=500, description="New description")
    category: Optional[str] = Field(
        None, max_length=50, description="New category")
    active: Optional[bool] = Field(None, description="Game active status")
    leaderboard_enabled: Optional[bool] = Field(
        None, description="Enable leaderboard")
    team_allowed: Optional[bool] = Field(
        None, description="Allow team participation")
