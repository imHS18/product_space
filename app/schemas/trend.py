"""
Trend schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class SentimentTrendResponse(BaseModel):
    """Schema for sentiment trend response"""
    id: int
    period_start: datetime
    period_end: datetime
    period_type: str
    channel: Optional[str]
    source: Optional[str]
    total_tickets: int
    positive_tickets: int
    negative_tickets: int
    neutral_tickets: int
    avg_sentiment: float
    avg_positive_score: float
    avg_negative_score: float
    avg_neutral_score: float
    avg_anger_score: float
    avg_confusion_score: float
    avg_delight_score: float
    avg_frustration_score: float
    sentiment_change: float
    trend_direction: str
    alerts_triggered: int
    critical_alerts: int
    avg_response_time_minutes: float
    resolution_rate: float
    calculated_at: datetime
    calculation_method: str
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    
    class Config:
        from_attributes = True


class TrendSummary(BaseModel):
    """Schema for trend summary"""
    time_period: str
    calculated_at: datetime
    trends: Dict[str, Dict[str, Any]]
