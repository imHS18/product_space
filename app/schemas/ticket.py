"""
Pydantic schemas for ticket-related operations
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class TicketBase(BaseModel):
    """Base ticket schema with common fields"""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    channel: str = Field(..., description="Communication channel (email, chat, phone, social)")
    source: str = Field(..., description="Source platform (zendesk, intercom, slack, etc.)")
    customer_id: Optional[str] = Field(None, description="Customer identifier")
    customer_email: Optional[str] = Field(None, description="Customer email address")
    customer_name: Optional[str] = Field(None, description="Customer name")
    subject: Optional[str] = Field(None, description="Ticket subject")
    content: str = Field(..., description="Ticket content/message")
    message_type: str = Field(default="message", description="Type of message")
    priority: str = Field(default="normal", description="Ticket priority")
    status: str = Field(default="open", description="Ticket status")
    assigned_to: Optional[str] = Field(None, description="Assigned agent")
    
    @validator('channel')
    def validate_channel(cls, v):
        valid_channels = ['email', 'chat', 'phone', 'social']
        if v not in valid_channels:
            raise ValueError(f'Channel must be one of: {valid_channels}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['open', 'pending', 'resolved', 'closed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v


class TicketCreate(TicketBase):
    """Schema for creating a new ticket"""
    pass


class TicketUpdate(BaseModel):
    """Schema for updating a ticket"""
    subject: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            valid_priorities = ['low', 'normal', 'high', 'urgent']
            if v not in valid_priorities:
                raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['open', 'pending', 'resolved', 'closed']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {valid_statuses}')
        return v


class SentimentSummary(BaseModel):
    """Sentiment summary for ticket response"""
    overall_sentiment: float
    is_negative: bool
    is_positive: bool
    is_neutral: bool
    analysis_method: str
    confidence_score: float


class AlertSummary(BaseModel):
    """Alert summary for ticket response"""
    alert_id: int
    alert_type: str
    severity: str
    title: str
    is_active: bool
    created_at: datetime


class TicketResponse(TicketBase):
    """Schema for ticket response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    resolved_at: Optional[datetime]
    processed: bool
    sentiment_analyzed: bool
    
    # Related data
    sentiment_analysis: Optional[SentimentSummary] = None
    active_alerts: List[AlertSummary] = []
    
    class Config:
        from_attributes = True


class TicketList(BaseModel):
    """Schema for paginated ticket list"""
    tickets: List[TicketResponse]
    total: int
    page: int
    size: int
    pages: int


class TicketBulkCreate(BaseModel):
    """Schema for bulk ticket creation"""
    tickets: List[TicketCreate] = Field(..., max_items=100)
    
    @validator('tickets')
    def validate_tickets(cls, v):
        if len(v) == 0:
            raise ValueError('At least one ticket must be provided')
        return v
