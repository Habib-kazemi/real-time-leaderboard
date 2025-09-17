import sys
import os
from feature.global_record.router import router as global_record_router
from fastapi import FastAPI
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

app = FastAPI(title="Global_record Service", version="1.0.0")

app.include_router(global_record_router, prefix="/v1")
