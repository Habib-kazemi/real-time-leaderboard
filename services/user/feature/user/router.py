from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from shared.config.settings import settings
from .model import UserModel
from .schema import UserCreate, UserResponse
from .service import login_user, register_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Extract user_id and permission from JWT token only."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        permission = payload.get("permission", [])
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "permission": permission}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    result = await register_user(user)
    user_data = await UserModel.get_user(result["user_id"])
    return user_data


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_user(form_data.username, form_data.password)


@router.get("/user/me", response_model=UserResponse)
async def get_current_user_endpoint(current_user: dict = Depends(get_current_user)):
    user = await UserModel.get_user(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
