import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.autonomy import autonomy_loop
from app.config import settings
from app.database import Base, engine
from app.routers.agent import router as agent_router


STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    task = None
    if settings.autonomy_enabled:
        task = asyncio.create_task(autonomy_loop())

    yield

    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(agent_router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health():
    return {"status": "ok", "autonomy_enabled": settings.autonomy_enabled}


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
