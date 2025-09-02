from fastapi import FastAPI

from feature.score.router import router as score_router


app = FastAPI(title="Score Service")


app.include_router(score_router)
