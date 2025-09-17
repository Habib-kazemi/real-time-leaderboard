import sys
import os
from feature.user.router import router as user_router
from fastapi import FastAPI
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

app = FastAPI(title="User Service", version="1.0.0")

app.include_router(user_router, prefix="/v1")
