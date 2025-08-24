"""
Alerts endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_alerts(
    page: int = 1,
    size: int = 20,
    severity: str = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of alerts
    """
    try:
        alert_service = AlertService(db)
        alerts, total = await alert_service.get_alerts_paginated(
            page=page,
            size=size,
            severity=severity,
            active_only=active_only
        )
        
        pages = (total + size - 1) // size
        
        return {
            "alerts": alerts,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}")
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific alert by ID
    """
    try:
        alert_service = AlertService(db)
        alert = await alert_service.get_alert_by_id(alert_id)
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
