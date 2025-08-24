"""
Trends endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.agent_manager import AgentManager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_trends(
    time_period: str = "1h",
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get sentiment trends for the specified time period
    """
    try:
        agent_manager: AgentManager = request.app.state.agent_manager
        
        result = await agent_manager.check_trends(time_period=time_period)
        
        return {
            "success": True,
            "trends": result
        }
        
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))
