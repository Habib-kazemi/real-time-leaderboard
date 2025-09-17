from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt

from shared.config.settings import settings
from .model import UserModel
from .schema import UserCreate, UserResponse
from .service import login_user, register_user

router = APIRouter(prefix="/v1")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


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


@router.get("/user/me", response_model=UserResponse)
async def get_current_user_endpoint(current_user: UserResponse = Depends(get_current_user)):
    """Return current user data."""
    return current_user
