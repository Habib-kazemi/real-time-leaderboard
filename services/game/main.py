import sys
import os
from feature.game.router import router as game_router
from fastapi import FastAPI
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

app = FastAPI(title="Game Service", version="1.0.0")

app.include_router(game_router, prefix="/v1")
