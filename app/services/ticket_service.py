"""
Ticket Service for database operations
"""

import logging
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.ticket import Ticket
from app.models.sentiment import SentimentAnalysis
from app.models.alert import Alert
from app.schemas.ticket import TicketCreate

logger = logging.getLogger(__name__)


class TicketService:
    """Service for ticket-related database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_ticket_with_analysis(
        self,
        ticket_data: TicketCreate,
        sentiment_result: Dict[str, Any],
        alerts: List[Dict] = None,
        response_recommendations: Dict[str, Any] = None
    ) -> Ticket:
        """Create a ticket with sentiment analysis and alerts"""
        try:
            # Create ticket
            ticket = Ticket(
                ticket_id=ticket_data.ticket_id,
                channel=ticket_data.channel,
                source=ticket_data.source,
                customer_id=ticket_data.customer_id,
                customer_email=ticket_data.customer_email,
                customer_name=ticket_data.customer_name,
                subject=ticket_data.subject,
                content=ticket_data.content,
                message_type=ticket_data.message_type,
                priority=ticket_data.priority,
                status=ticket_data.status,
                assigned_to=ticket_data.assigned_to,
                processed=True,
                sentiment_analyzed=True
            )
            
            self.db.add(ticket)
            await self.db.flush()  # Get the ticket ID
            
            # Create sentiment analysis
            sentiment_analysis = SentimentAnalysis(
                ticket_id=ticket.id,
                overall_sentiment=sentiment_result["overall_sentiment"],
                positive_score=sentiment_result["positive_score"],
                negative_score=sentiment_result["negative_score"],
                neutral_score=sentiment_result["neutral_score"],
                anger_score=sentiment_result.get("anger_score", 0.0),
                confusion_score=sentiment_result.get("confusion_score", 0.0),
                delight_score=sentiment_result.get("delight_score", 0.0),
                frustration_score=sentiment_result.get("frustration_score", 0.0),
                analysis_method=sentiment_result["analysis_method"],
                confidence_score=sentiment_result["confidence_score"],
                processing_time_ms=sentiment_result["processing_time_ms"],
                keywords=sentiment_result.get("keywords", []),
                entities=sentiment_result.get("entities", []),
                topics=sentiment_result.get("topics", []),
                analyzed_by_agent="sentiment_analyzer"
            )
            
            self.db.add(sentiment_analysis)
            await self.db.flush()
            
            # Create alerts if any
            if alerts:
                for alert_data in alerts:
                    if alert_data.get("should_alert"):
                        alert = Alert(
                            ticket_id=ticket.id,
                            sentiment_analysis_id=sentiment_analysis.id,
                            alert_type=alert_data["alert_type"],
                            severity=alert_data["severity"],
                            threshold_breached=alert_data["threshold_breached"],
                            title=alert_data["title"],
                            message=alert_data["message"],
                            recommendations=alert_data.get("recommendations"),
                            sent_to_slack=alert_data.get("sent_to_slack", False),
                            triggered_by_agent="alert_manager",
                            alert_data=alert_data.get("alert_data", {})
                        )
                        self.db.add(alert)
            
            await self.db.commit()
            
            # Return ticket with relationships
            return await self.get_ticket_by_id(ticket.ticket_id)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating ticket with analysis: {e}")
            raise
    
    async def get_tickets_paginated(
        self,
        page: int = 1,
        size: int = 20,
        channel: str = None,
        source: str = None,
        status: str = None,
        priority: str = None
    ) -> Tuple[List[Ticket], int]:
        """Get paginated tickets with filters"""
        try:
            # Build query
            query = select(Ticket).options(
                selectinload(Ticket.sentiment_analyses),
                selectinload(Ticket.alerts)
            )
            
            # Add filters
            if channel:
                query = query.where(Ticket.channel == channel)
            if source:
                query = query.where(Ticket.source == source)
            if status:
                query = query.where(Ticket.status == status)
            if priority:
                query = query.where(Ticket.priority == priority)
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results
            query = query.order_by(Ticket.created_at.desc())
            query = query.offset((page - 1) * size).limit(size)
            
            result = await self.db.execute(query)
            tickets = result.scalars().all()
            
            return list(tickets), total
            
        except Exception as e:
            logger.error(f"Error getting tickets paginated: {e}")
            raise
    
    async def get_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ticket_id"""
        try:
            query = select(Ticket).options(
                selectinload(Ticket.sentiment_analyses),
                selectinload(Ticket.alerts)
            ).where(Ticket.ticket_id == ticket_id)
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting ticket by ID: {e}")
            raise
    
    async def get_ticket_sentiment(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get sentiment analysis for a ticket"""
        try:
            ticket = await self.get_ticket_by_id(ticket_id)
            if not ticket or not ticket.sentiment_analyses:
                return None
            
            sentiment = ticket.sentiment_analyses[0]  # Get the latest analysis
            return {
                "overall_sentiment": sentiment.overall_sentiment,
                "positive_score": sentiment.positive_score,
                "negative_score": sentiment.negative_score,
                "neutral_score": sentiment.neutral_score,
                "anger_score": sentiment.anger_score,
                "confusion_score": sentiment.confusion_score,
                "delight_score": sentiment.delight_score,
                "frustration_score": sentiment.frustration_score,
                "analysis_method": sentiment.analysis_method,
                "confidence_score": sentiment.confidence_score,
                "keywords": sentiment.keywords,
                "topics": sentiment.topics,
                "created_at": sentiment.created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting ticket sentiment: {e}")
            raise
    
    async def get_ticket_alerts(self, ticket_id: str) -> List[Dict[str, Any]]:
        """Get alerts for a ticket"""
        try:
            ticket = await self.get_ticket_by_id(ticket_id)
            if not ticket:
                return []
            
            alerts = []
            for alert in ticket.alerts:
                alerts.append({
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "message": alert.message,
                    "is_active": alert.is_active,
                    "created_at": alert.created_at
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting ticket alerts: {e}")
            raise
