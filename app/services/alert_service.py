"""
Alert Service for database operations
"""

import logging
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.alert import Alert
from app.models.ticket import Ticket

logger = logging.getLogger(__name__)


class AlertService:
    """Service for alert-related database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_alerts_paginated(
        self,
        page: int = 1,
        size: int = 20,
        severity: str = None,
        active_only: bool = True
    ) -> Tuple[List[Alert], int]:
        """Get paginated alerts with filters"""
        try:
            # Build query
            query = select(Alert).options(
                selectinload(Alert.ticket),
                selectinload(Alert.sentiment_analysis)
            )
            
            # Add filters
            if severity:
                query = query.where(Alert.severity == severity)
            if active_only:
                query = query.where(Alert.resolved_at.is_(None))
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Get paginated results
            query = query.order_by(Alert.created_at.desc())
            query = query.offset((page - 1) * size).limit(size)
            
            result = await self.db.execute(query)
            alerts = result.scalars().all()
            
            return list(alerts), total
            
        except Exception as e:
            logger.error(f"Error getting alerts paginated: {e}")
            raise
    
    async def get_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        """Get alert by ID"""
        try:
            query = select(Alert).options(
                selectinload(Alert.ticket),
                selectinload(Alert.sentiment_analysis)
            ).where(Alert.id == alert_id)
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting alert by ID: {e}")
            raise
