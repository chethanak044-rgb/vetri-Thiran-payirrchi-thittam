from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_settings().ensure_directories()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", description="AI Comic Story Creator using Gemini and image-generation backends", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(settings.static_path)), name="static")
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "image_provider": settings.image_provider}
