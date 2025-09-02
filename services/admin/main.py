from fastapi import FastAPI

from feature.admin.router import router as admin_router


app = FastAPI(title="Admin Service")


app.include_router(admin_router)
