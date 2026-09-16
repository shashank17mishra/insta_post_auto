"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes_generate import router as generate_router
from app.api.routes_health import router as health_router
from app.api.routes_posts import router as posts_router
from app.api.routes_settings import router as settings_router
from app.api.routes_topics import router as topics_router
from app.config import settings
from app.database.db import init_db
from app.database.repository import Repository
from app.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    logger.info("Initializing StudyNotes AutoPoster Application...")
    settings.ensure_directories()
    init_db()

    # Seed topics if database is empty
    repo = Repository()
    stats = repo.get_dashboard_stats()
    if stats["total_topics"] == 0 and settings.topics_file_path.exists():
        repo.seed_topics_from_file(settings.topics_file_path)

    yield
    logger.info("Shutting down StudyNotes AutoPoster Application...")


app = FastAPI(
    title="StudyNotes AutoPoster",
    description="Automated educational Instagram content-generation and publishing system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router)
app.include_router(topics_router)
app.include_router(generate_router)
app.include_router(posts_router)
app.include_router(settings_router)

# Static file mounts
generated_dir = settings.output_dir
generated_dir.mkdir(parents=True, exist_ok=True)
app.mount("/generated", StaticFiles(directory=str(generated_dir)), name="generated")

frontend_dir = settings.project_root / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/", include_in_schema=False)
def serve_dashboard():
    """Serve the single-page web dashboard."""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "name": "StudyNotes AutoPoster API",
        "docs_url": "/docs",
        "health_url": "/api/health",
    }
