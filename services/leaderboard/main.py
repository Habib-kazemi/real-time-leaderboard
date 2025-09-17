import sys
import os
from feature.leaderboard.router import router as leaderboard_router
from fastapi import FastAPI
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

app = FastAPI(title="Leaderboard Service", version="1.0.0")

app.include_router(leaderboard_router, prefix="/v1")
