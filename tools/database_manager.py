"""
Database Manager Tool
Handles database operations and data persistence for the sentiment analysis system
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from crewai.tools import BaseTool

from app.core.database import get_db
from app.models.ticket import Ticket
from app.models.sentiment import SentimentAnalysis
from app.models.alert import Alert
from app.models.trend import SentimentTrend

logger = logging.getLogger(__name__)


class DatabaseManager(BaseTool):
    """Tool for managing database operations and data persistence"""
    
    name: str = "Database Manager"
    description: str = "Handles database operations including saving tickets, sentiment analysis results, alerts, and trend data."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'db_session', None)
    
    def _run(self, operation: str, data: str) -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        # In practice, you'd convert the strings back to dicts or handle JSON
        # For now, returning a simple database operation result
        return f"Database operation {operation} completed"
    
    async def save_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save ticket to database"""
        try:
            async for db in get_db():
                # Create ticket object
                ticket = Ticket(
                    ticket_id=ticket_data["id"],
                    content=ticket_data["content"],
                    customer_email=ticket_data["customer_id"],
                    channel=ticket_data["channel"],
                    source=ticket_data["source"],
                    priority=ticket_data["priority"],
                    created_at=datetime.fromisoformat(ticket_data["created_at"].replace('Z', '+00:00')),
                    metadata=ticket_data.get("metadata", {})
                )
                
                db.add(ticket)
                await db.commit()
                await db.refresh(ticket)
                
                logger.info(f"Ticket saved successfully: {ticket_data['id']}")
                return {"success": True, "ticket_id": ticket_data["id"]}
                
        except Exception as e:
            logger.error(f"Error saving ticket: {e}")
            return {"success": False, "error": str(e)}
    
    async def save_sentiment_analysis(self, ticket_id: str, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save sentiment analysis results"""
        try:
            async for db in get_db():
                sentiment = SentimentAnalysis(
                    ticket_id=ticket_id,
                    sentiment_score=sentiment_data.get("sentiment_score", 0.0),
                    sentiment_label=sentiment_data.get("sentiment_label", "neutral"),
                    confidence=sentiment_data.get("confidence", 0.0),
                    emotions=sentiment_data.get("emotions", {}),
                    keywords=sentiment_data.get("keywords", []),
                    analysis_methods=sentiment_data.get("analysis_methods", []),
                    raw_output=sentiment_data.get("raw_output", {}),
                    created_at=datetime.now()
                )
                
                db.add(sentiment)
                await db.commit()
                await db.refresh(sentiment)
                
                logger.info(f"Sentiment analysis saved for ticket: {ticket_id}")
                return {"success": True, "sentiment_id": sentiment.id}
                
        except Exception as e:
            logger.error(f"Error saving sentiment analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def save_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save alert to database"""
        try:
            async for db in get_db():
                alert = Alert(
                    ticket_id=alert_data["ticket_id"],
                    alert_type=alert_data["alert_type"],
                    severity=alert_data["severity"],
                    message=alert_data["message"],
                    triggered_at=datetime.now(),
                    metadata=alert_data.get("metadata", {})
                )
                
                db.add(alert)
                await db.commit()
                await db.refresh(alert)
                
                logger.info(f"Alert saved: {alert_data['alert_type']} for ticket {alert_data['ticket_id']}")
                return {"success": True, "alert_id": alert.id}
                
        except Exception as e:
            logger.error(f"Error saving alert: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_trends(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update sentiment trends"""
        try:
            async for db in get_db():
                # Get current trend for the time period
                time_period = trend_data["time_period"]
                current_time = datetime.now()
                
                # Round to appropriate time period
                if time_period == "1h":
                    rounded_time = current_time.replace(minute=0, second=0, microsecond=0)
                elif time_period == "1d":
                    rounded_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    rounded_time = current_time.replace(minute=0, second=0, microsecond=0)
                
                # Check if trend exists for this period
                stmt = select(SentimentTrend).where(
                    SentimentTrend.time_period == time_period,
                    SentimentTrend.period_start == rounded_time
                )
                result = await db.execute(stmt)
                existing_trend = result.scalar_one_or_none()
                
                if existing_trend:
                    # Update existing trend
                    existing_trend.total_tickets += trend_data.get("total_tickets", 1)
                    existing_trend.positive_sentiment += trend_data.get("positive_sentiment", 0)
                    existing_trend.negative_sentiment += trend_data.get("negative_sentiment", 0)
                    existing_trend.neutral_sentiment += trend_data.get("neutral_sentiment", 0)
                    existing_trend.alerts_triggered += trend_data.get("alerts_triggered", 0)
                    existing_trend.updated_at = current_time
                else:
                    # Create new trend
                    trend = SentimentTrend(
                        time_period=time_period,
                        period_start=rounded_time,
                        total_tickets=trend_data.get("total_tickets", 1),
                        positive_sentiment=trend_data.get("positive_sentiment", 0),
                        negative_sentiment=trend_data.get("negative_sentiment", 0),
                        neutral_sentiment=trend_data.get("neutral_sentiment", 0),
                        alerts_triggered=trend_data.get("alerts_triggered", 0),
                        created_at=current_time,
                        updated_at=current_time
                    )
                    db.add(trend)
                
                await db.commit()
                logger.info(f"Trends updated for period: {time_period}")
                return {"success": True, "time_period": time_period}
                
        except Exception as e:
            logger.error(f"Error updating trends: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_recent_tickets(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent tickets from database"""
        try:
            async for db in get_db():
                cutoff_time = datetime.now() - timedelta(hours=hours)
                stmt = select(Ticket).where(Ticket.created_at >= cutoff_time)
                result = await db.execute(stmt)
                tickets = result.scalars().all()
                
                return [
                    {
                        "id": ticket.ticket_id,
                        "content": ticket.content,
                        "customer_email": ticket.customer_email,
                        "channel": ticket.channel,
                        "priority": ticket.priority,
                        "created_at": ticket.created_at.isoformat(),
                        "metadata": ticket.metadata
                    }
                    for ticket in tickets
                ]
                
        except Exception as e:
            logger.error(f"Error getting recent tickets: {e}")
            return []
    
    async def get_sentiment_history(self, ticket_id: str) -> List[Dict[str, Any]]:
        """Get sentiment analysis history for a ticket"""
        try:
            async for db in get_db():
                stmt = select(SentimentAnalysis).where(SentimentAnalysis.ticket_id == ticket_id)
                result = await db.execute(stmt)
                analyses = result.scalars().all()
                
                return [
                    {
                        "sentiment_score": analysis.sentiment_score,
                        "sentiment_label": analysis.sentiment_label,
                        "confidence": analysis.confidence,
                        "emotions": analysis.emotions,
                        "keywords": analysis.keywords,
                        "created_at": analysis.created_at.isoformat()
                    }
                    for analysis in analyses
                ]
                
        except Exception as e:
            logger.error(f"Error getting sentiment history: {e}")
            return []
    
    async def get_trends(self, time_period: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get sentiment trends for a time period"""
        try:
            async for db in get_db():
                cutoff_time = datetime.now() - timedelta(hours=hours)
                stmt = select(SentimentTrend).where(
                    SentimentTrend.time_period == time_period,
                    SentimentTrend.period_start >= cutoff_time
                ).order_by(SentimentTrend.period_start)
                
                result = await db.execute(stmt)
                trends = result.scalars().all()
                
                return [
                    {
                        "period_start": trend.period_start.isoformat(),
                        "total_tickets": trend.total_tickets,
                        "positive_sentiment": trend.positive_sentiment,
                        "negative_sentiment": trend.negative_sentiment,
                        "neutral_sentiment": trend.neutral_sentiment,
                        "alerts_triggered": trend.alerts_triggered
                    }
                    for trend in trends
                ]
                
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return []
    
    async def cleanup_old_data(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old data from database"""
        try:
            async for db in get_db():
                cutoff_time = datetime.now() - timedelta(days=days)
                
                # Delete old tickets
                stmt = delete(Ticket).where(Ticket.created_at < cutoff_time)
                result = await db.execute(stmt)
                tickets_deleted = result.rowcount
                
                # Delete old sentiment analyses
                stmt = delete(SentimentAnalysis).where(SentimentAnalysis.created_at < cutoff_time)
                result = await db.execute(stmt)
                analyses_deleted = result.rowcount
                
                # Delete old alerts
                stmt = delete(Alert).where(Alert.triggered_at < cutoff_time)
                result = await db.execute(stmt)
                alerts_deleted = result.rowcount
                
                await db.commit()
                
                logger.info(f"Cleanup completed: {tickets_deleted} tickets, {analyses_deleted} analyses, {alerts_deleted} alerts deleted")
                return {
                    "success": True,
                    "tickets_deleted": tickets_deleted,
                    "analyses_deleted": analyses_deleted,
                    "alerts_deleted": alerts_deleted
                }
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {"success": False, "error": str(e)}
