from fastapi import FastAPI

from feature.game.router import router as game_router
from feature.global_record.router import router as global_record_router
from feature.leaderboard.router import router as leaderboard_router
from feature.score.router import router as score_router
from feature.user.router import router as user_router


app = FastAPI(title="Real-Time Leaderboard API")


app.include_router(user_router)
app.include_router(game_router)
app.include_router(score_router)
app.include_router(leaderboard_router)
app.include_router(global_record_router)
