import sys
import os
from feature.score.router import router as score_router
from fastapi import FastAPI
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

app = FastAPI(title="Score Service", version="1.0.0")

app.include_router(score_router, prefix="/v1")
