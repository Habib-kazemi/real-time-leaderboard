from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr, Field
from config.permissions import Permission


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, description="User password")
    email: EmailStr | None = Field(None, description="Optional email address")
    full_name: str | None = Field(
        None, max_length=100, description="Optional full name")
    country: str | None = Field(
        None, max_length=2, description="ISO 3166-1 alpha-2 country code")
    type: str = Field(..., pattern="^(individual|team)$",
                      description="User type: individual or team")
    team_member: List[str] = Field(
        default_factory=list, description="List of team member user IDs")
    permission: List[Permission] = Field(
        default=[Permission.CAN_SUBMIT_SCORE, Permission.CAN_VIEW_LEADERBOARD],
        description="List of user permissions"
    )


class UserResponse(BaseModel):
    """Schema for returning user data."""
    user_id: str
    username: str
    email: EmailStr | None
    full_name: str | None
    country: str | None
    type: str
    team_member: List[str]
    total_score: int
    level: int
    created_at: datetime
    permission: List[Permission]
