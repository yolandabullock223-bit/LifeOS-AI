"""
LifeOS AI - Main Application Entry Point

FastAPI application with orchestration, security, and middleware setup.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.config.settings import Settings
from app.config.logging import setup_logging
from app.services.orchestrator import CentralOrchestrator

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Settings
settings = Settings()

# Central Orchestrator
orchestrator = CentralOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting LifeOS AI Application")
    await orchestrator.initialize_all_services()
    yield
    # Shutdown
    logger.info("Shutting down LifeOS AI Application")
    await orchestrator.shutdown_all_services()


# Create FastAPI application
app = FastAPI(
    title="LifeOS AI",
    description="Production-grade AI learning platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)


# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Application health check endpoint."""
    health = await orchestrator.health_check()
    return {
        "status": "healthy" if health["status"] == "healthy" else "degraded",
        "services": health["services"],
        "timestamp": health.get("timestamp"),
    }


# Root Endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LifeOS AI - Production-grade learning platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        },
    )


# Import routes (to be added)
# from app.api import auth, users, coach, curriculum, progress, analytics, avatar, world


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
