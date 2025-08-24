"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import tickets, sentiment, alerts, trends, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(trends.router, prefix="/trends", tags=["trends"])
