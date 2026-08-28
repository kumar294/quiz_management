from fastapi import FastAPI

from app.api.routes import router
from app.models.db import init_db

app = FastAPI(title="GLIM Placement Prep — Multi-Agent API", version="0.1.0")
app.include_router(router)


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
