from fastapi import FastAPI

from feature.user.router import router as user_router


app = FastAPI(title="Real-Time Leaderboard - Auth Service")


app.include_router(user_router)
