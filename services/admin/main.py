import sys
import os
from feature.admin.router import router as admin_router
from fastapi import FastAPI
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

app = FastAPI(title="Admin Service", version="1.0.0")

app.include_router(admin_router, prefix="/v1")
