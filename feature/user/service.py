from datetime import datetime, timedelta
from fastapi import HTTPException
from passlib.context import CryptContext
from jose import jwt

from config.database import get_postgres_conn
from config.settings import settings
from feature.user.model import UserModel
from feature.user.schema import UserCreate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def register_user(user: UserCreate) -> dict:
    """Register a new user with hashed password."""
    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT username FROM user WHERE username = %s", (user.username,))
            if cur.fetchone():
                raise HTTPException(
                    status_code=400, detail="Username already exists")
    finally:
        conn.close()

    hashed_password = pwd_context.hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    user_data["total_score"] = 0
    user_data["level"] = 1

    user_id = await UserModel.create_user(user_data)
    return {"user_id": user_id, "message": "User registered successfully"}


async def login_user(username: str, password: str) -> dict:
    """Authenticate user and generate JWT token."""
    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, password, permission FROM user WHERE username = %s", (username,))
            user = cur.fetchone()
            if not user or not pwd_context.verify(password, user["password"]):
                raise HTTPException(
                    status_code=401, detail="Invalid credentials")
            user_id, _, permissions = user["user_id"], user["password"], json.loads(
                user["permission"])
    finally:
        conn.close()

    token = jwt.encode(
        {"sub": user_id, "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=24)},
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    return {"access_token": token, "token_type": "bearer"}
