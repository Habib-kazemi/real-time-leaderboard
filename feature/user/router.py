from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt

from config.settings import settings
from feature.user.model import UserModel
from feature.user.schema import UserCreate, UserResponse
from feature.user.service import login_user, register_user


router = APIRouter(prefix="/v1")


async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/v1/login"))):
    """Extract user data from JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await UserModel.get_user(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user."""
    result = await register_user(user)
    user_data = await UserModel.get_user(result["user_id"])
    return user_data


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token."""
    return await login_user(form_data.username, form_data.password)
