from fastapi import FastAPI

from feature.game.router import router as game_router


app = FastAPI(title="Game Service")


app.include_router(game_router)
