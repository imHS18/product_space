#!/usr/bin/env python3
"""
Debug ticket processing workflow directly
"""

import sys
sys.path.append('.')

from app.services.agent_manager import AgentManager
from app.schemas.ticket import TicketCreate
import asyncio

async def test_ticket_processing():
    """Test ticket processing directly"""
    print("Testing ticket processing workflow directly...")
    
    # Create agent manager
    agent_manager = AgentManager()
    
    # Initialize it
    await agent_manager.initialize()
    
    # Create a test ticket
    ticket_data = TicketCreate(
        ticket_id="DEBUG-001",
        content="I am extremely frustrated with your service!",
        customer_email="test@example.com",
        channel="email",
        source="support_portal",
        priority="high"
    )
    
    try:
        # Process the ticket
        result = await agent_manager.process_ticket(ticket_data)
        print("✅ Ticket processing successful!")
        print(f"Result keys: {list(result.keys())}")
        print(f"Sentiment analysis: {result.get('sentiment_analysis', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error processing ticket: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ticket_processing())
