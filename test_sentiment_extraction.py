#!/usr/bin/env python3
"""
Test script to verify sentiment extraction is working correctly
"""

import sys
import asyncio
from datetime import datetime

# Add the current directory to the path
sys.path.append('.')

from app.services.agent_manager import AgentManager
from app.schemas.ticket import TicketCreate

async def test_sentiment_extraction():
    print("Testing sentiment extraction with AgentManager...")
    
    # Initialize the agent manager
    agent_manager = AgentManager()
    await agent_manager.initialize()
    
    # Create a test ticket
    ticket_data = TicketCreate(
        ticket_id="test-sentiment-001",
        content="The product arrived damaged and I am extremely frustrated. I need a replacement immediately! This is unacceptable and I demand a solution. The packaging was terrible and the delivery was delayed. I've been a loyal customer for years and this is the worst experience I've had. I am very angry and disappointed.",
        customer_email="test@example.com",
        channel="email",
        source="test",
        priority="high"
    )
    
    try:
        # Process the ticket
        result = await agent_manager.process_ticket(ticket_data)
        
        print("\n=== WORKFLOW RESULT ===")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Check sentiment analysis
        sentiment_analysis = result.get('sentiment_analysis', {})
        print(f"\n=== SENTIMENT ANALYSIS ===")
        print(f"Sentiment analysis type: {type(sentiment_analysis)}")
        print(f"Sentiment analysis: {sentiment_analysis}")
        
        # Check if sentiment score is correct
        sentiment_score = sentiment_analysis.get('sentiment_score', 0.0)
        confidence = sentiment_analysis.get('confidence', 0.0)
        
        print(f"\n=== EXTRACTED VALUES ===")
        print(f"Sentiment Score: {sentiment_score}")
        print(f"Confidence: {confidence}")
        print(f"Sentiment Label: {sentiment_analysis.get('sentiment_label', 'unknown')}")
        print(f"Is Negative: {sentiment_analysis.get('is_negative', False)}")
        print(f"Is Positive: {sentiment_analysis.get('is_positive', False)}")
        
        # Check if the sentiment score is correct (should be around -0.77)
        if sentiment_score < -0.5:
            print("✅ SUCCESS: Sentiment score is correctly negative!")
        else:
            print("❌ FAILED: Sentiment score is not negative enough")
            print(f"Expected: < -0.5, Got: {sentiment_score}")
        
        # Check confidence
        if confidence > 0.7:
            print("✅ SUCCESS: Confidence is high!")
        else:
            print("❌ FAILED: Confidence is too low")
            print(f"Expected: > 0.7, Got: {confidence}")
        
        # Check workflow output
        workflow_output = result.get('workflow_output', {})
        print(f"\n=== WORKFLOW OUTPUT ===")
        print(f"Workflow output type: {type(workflow_output)}")
        if isinstance(workflow_output, dict):
            print(f"Workflow output keys: {list(workflow_output.keys())}")
        else:
            print(f"Workflow output: {workflow_output}")
        
    except Exception as e:
        print(f"❌ Error processing ticket: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await agent_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(test_sentiment_extraction())
