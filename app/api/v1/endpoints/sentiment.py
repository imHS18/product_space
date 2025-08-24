"""
Sentiment analysis endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.services.agent_manager import AgentManager

logger = logging.getLogger(__name__)
router = APIRouter()


class SentimentRequest(BaseModel):
    text: str
    context: dict = None


@router.post("/analyze")
async def analyze_sentiment(
    sentiment_request: SentimentRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze sentiment of text content
    """
    try:
        agent_manager: AgentManager = request.app.state.agent_manager
        
        result = await agent_manager.analyze_sentiment_only(
            content=sentiment_request.text,
            context=sentiment_request.context or {}
        )
        
        return {
            "success": True,
            "sentiment_analysis": result
        }
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
