"""Main FastAPI application for NagarSeva Backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

from app.config import settings
from app.routers import (
    complaints_router,
    heatmap_router,
    routes_router,
    escalation_router,
    auth_router,
)
from app.utils.database import close_mongo_connection, create_indexes, get_database, seed_default_data

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _configured_label(value: Optional[str]) -> str:
    """Return a safe label for sensitive connection settings."""
    return "configured" if value else "not configured"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("NagarSeva Backend starting...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"MongoDB: {_configured_label(settings.mongodb_url)}")
    logger.info(f"Redis: {_configured_label(settings.redis_url)}")

    # Initialize MongoDB indexes
    try:
        db = await get_database()
        await create_indexes(db)
        await seed_default_data(db)
        logger.info("✅ MongoDB indexes initialized")
    except Exception as e:
        logger.error(f"⚠️ Error initializing MongoDB indexes: {e}")
        # Don't fail startup if indexes fail
        logger.warning("Continuing without indexes (non-critical)")

    # Initialize Celery
    try:
        logger.info("Celery integration ready")
    except Exception as e:
        logger.error(f"Error initializing Celery: {e}")

    yield

    # Shutdown
    logger.info("NagarSeva Backend shutting down...")
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
cors_origins = [
    origin.strip() for origin in settings.cors_origins.split(",")
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded complaint media for dashboard previews.
upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

# Include routers
app.include_router(auth_router)
app.include_router(complaints_router)
app.include_router(heatmap_router)
app.include_router(routes_router)
app.include_router(escalation_router)


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "NagarSeva Backend",
        "version": settings.api_version,
    }


# Info endpoint
@app.get("/info")
async def get_info() -> dict:
    """Get API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "environment": settings.environment,
        "agents": [
            "1. Multimodal Issue Intelligence",
            "2. Authority Router",
            "3. Safety Heatmap & Analytics",
            "4. Safer Route Advisor",
            "5. Autonomous Escalation",
        ],
    }


# Root endpoint
@app.get("/")
async def root() -> dict:
    """Root endpoint with API overview."""
    return {
        "message": "Welcome to NagarSeva Backend",
        "version": settings.api_version,
        "endpoints": {
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
            "info": "/info",
            "complaints": "/api/complaints",
            "heatmap": "/api/heatmap",
            "routes": "/api/routes",
            "escalation": "/api/escalation",
        },
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.debug else "An error occurred",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
