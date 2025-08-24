"""
Alert schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class AlertCreate(BaseModel):
    """Schema for creating alerts"""
    ticket_id: int
    sentiment_analysis_id: int
    alert_type: str
    severity: str
    threshold_breached: float
    title: str
    message: str
    recommendations: Optional[str] = None
    triggered_by_agent: Optional[str] = None
    alert_data: Optional[Dict[str, Any]] = None


class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    ticket_id: int
    sentiment_analysis_id: int
    alert_type: str
    severity: str
    threshold_breached: float
    title: str
    message: str
    recommendations: Optional[str]
    sent_to_slack: bool
    slack_message_id: Optional[str]
    sent_to_email: bool
    email_sent_at: Optional[datetime]
    triggered_by_agent: Optional[str]
    alert_data: Optional[Dict[str, Any]]
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    is_active: bool
    is_acknowledged: bool
    
    class Config:
        from_attributes = True


class AlertList(BaseModel):
    """Schema for paginated alert list"""
    alerts: List[AlertResponse]
    total: int
    page: int
    size: int
    pages: int
