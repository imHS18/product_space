"""
FastAPI Customer Sentiment Watchdog System
Main application entry point with async setup and route registration
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.core.logging import setup_logging
from app.services.agent_manager import AgentManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown"""
    # Startup
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Customer Sentiment Watchdog System")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize agent manager
    app.state.agent_manager = AgentManager()
    await app.state.agent_manager.initialize()
    logger.info("AI Agents initialized")
    
    yield
    
    # Shutdown
    if hasattr(app.state, 'agent_manager'):
        await app.state.agent_manager.cleanup()
    logger.info("Shutting down Customer Sentiment Watchdog System")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Customer Sentiment Watchdog",
        description="Real-time sentiment analysis and alert system for customer support",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)}
        )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "sentiment-watchdog"}
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
