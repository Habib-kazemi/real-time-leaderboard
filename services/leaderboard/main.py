from fastapi import FastAPI

from feature.leaderboard.router import router as leaderboard_router


app = FastAPI(title="Leaderboard Service")


app.include_router(leaderboard_router)
