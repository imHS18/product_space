"""
Sentiment analysis schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SentimentAnalysisCreate(BaseModel):
    """Schema for creating sentiment analysis"""
    ticket_id: int
    overall_sentiment: float
    positive_score: float
    negative_score: float
    neutral_score: float
    anger_score: float = 0.0
    confusion_score: float = 0.0
    delight_score: float = 0.0
    frustration_score: float = 0.0
    analysis_method: str
    confidence_score: float = 1.0
    processing_time_ms: int = 0
    keywords: Optional[List[str]] = None
    entities: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    analyzed_by_agent: Optional[str] = None


class SentimentAnalysisResponse(BaseModel):
    """Schema for sentiment analysis response"""
    id: int
    ticket_id: int
    overall_sentiment: float
    positive_score: float
    negative_score: float
    neutral_score: float
    anger_score: float
    confusion_score: float
    delight_score: float
    frustration_score: float
    analysis_method: str
    confidence_score: float
    processing_time_ms: int
    keywords: Optional[List[str]]
    entities: Optional[List[str]]
    topics: Optional[List[str]]
    analyzed_by_agent: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
