"""
Tickets API endpoints for processing customer support tickets
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.ticket import TicketCreate, TicketResponse, TicketList, TicketBulkCreate
from app.services.ticket_service import TicketService
from app.services.agent_manager import AgentManager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=dict)
async def create_ticket(
    ticket_data: TicketCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new ticket and process it through the sentiment analysis pipeline
    """
    try:
        # Get agent manager from app state
        agent_manager: AgentManager = request.app.state.agent_manager
        
        # Process ticket through AI pipeline
        result = await agent_manager.process_ticket(ticket_data)
        
        # Save to database
        ticket_service = TicketService(db)
        saved_ticket = await ticket_service.create_ticket_with_analysis(
            ticket_data=ticket_data,
            sentiment_result=result["sentiment_analysis"],
            alerts=result.get("alerts", []),
            response_recommendations=result.get("response_recommendations")
        )
        
        return {
            "success": True,
            "message": "Ticket processed successfully",
            "ticket": saved_ticket,
            "processing_metadata": result["processing_metadata"]
        }
        
    except Exception as e:
        logger.error(f"Error processing ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=dict)
async def create_tickets_bulk(
    bulk_data: TicketBulkCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple tickets in bulk
    """
    try:
        agent_manager: AgentManager = request.app.state.agent_manager
        ticket_service = TicketService(db)
        
        results = []
        for ticket_data in bulk_data.tickets:
            try:
                # Process ticket through AI pipeline
                result = await agent_manager.process_ticket(ticket_data)
                
                # Save to database
                saved_ticket = await ticket_service.create_ticket_with_analysis(
                    ticket_data=ticket_data,
                    sentiment_result=result["sentiment_analysis"],
                    alerts=result.get("alerts", []),
                    response_recommendations=result.get("response_recommendations")
                )
                
                results.append({
                    "success": True,
                    "ticket_id": ticket_data.ticket_id,
                    "processing_metadata": result["processing_metadata"]
                })
                
            except Exception as e:
                logger.error(f"Error processing ticket {ticket_data.ticket_id}: {e}")
                results.append({
                    "success": False,
                    "ticket_id": ticket_data.ticket_id,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"Processed {len(bulk_data.tickets)} tickets",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk ticket processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=TicketList)
async def get_tickets(
    page: int = 1,
    size: int = 20,
    channel: str = None,
    source: str = None,
    status: str = None,
    priority: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of tickets with optional filters
    """
    try:
        ticket_service = TicketService(db)
        tickets, total = await ticket_service.get_tickets_paginated(
            page=page,
            size=size,
            channel=channel,
            source=source,
            status=status,
            priority=priority
        )
        
        pages = (total + size - 1) // size
        
        return TicketList(
            tickets=tickets,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific ticket by ID
    """
    try:
        ticket_service = TicketService(db)
        ticket = await ticket_service.get_ticket_by_id(ticket_id)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return ticket
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticket_id}/sentiment")
async def get_ticket_sentiment(
    ticket_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get sentiment analysis for a specific ticket
    """
    try:
        ticket_service = TicketService(db)
        sentiment = await ticket_service.get_ticket_sentiment(ticket_id)
        
        if not sentiment:
            raise HTTPException(status_code=404, detail="Sentiment analysis not found")
        
        return sentiment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sentiment for ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticket_id}/alerts")
async def get_ticket_alerts(
    ticket_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get alerts for a specific ticket
    """
    try:
        ticket_service = TicketService(db)
        alerts = await ticket_service.get_ticket_alerts(ticket_id)
        
        return {"alerts": alerts}
        
    except Exception as e:
        logger.error(f"Error getting alerts for ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
