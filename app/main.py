"""FitBuddy FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import ROOT_DIR
from .database import init_db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="FitBuddy — AI Fitness Plan Generator", description="Personalized workout plans and nutrition guidance.", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "static")), name="static")
app.include_router(router)


@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}
