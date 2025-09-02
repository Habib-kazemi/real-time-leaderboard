from fastapi import FastAPI

from feature.global_record.router import router as global_record_router


app = FastAPI(title="Global Record Service")


app.include_router(global_record_router)
