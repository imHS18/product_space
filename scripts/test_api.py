#!/usr/bin/env python3
"""
Test script for the Customer Sentiment Watchdog API
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import random

API_BASE = "http://localhost:8000/api/v1"

# Sample ticket data for testing
SAMPLE_TICKETS = [
    {
        "ticket_id": "TICKET-001",
        "channel": "email",
        "source": "zendesk",
        "customer_id": "CUST-001",
        "customer_email": "angry.customer@example.com",
        "customer_name": "John Smith",
        "subject": "Very frustrated with service",
        "content": "I am extremely angry and frustrated with your terrible service! I've been waiting for 3 days and nobody has responded to my urgent request. This is completely unacceptable and I want to speak to a manager immediately. I'm considering canceling my subscription and leaving a negative review everywhere.",
        "message_type": "message",
        "priority": "urgent",
        "status": "open"
    },
    {
        "ticket_id": "TICKET-002",
        "channel": "chat",
        "source": "intercom",
        "customer_id": "CUST-002",
        "customer_email": "confused.user@example.com",
        "customer_name": "Sarah Johnson",
        "subject": "Need help with setup",
        "content": "Hi, I'm a bit confused about how to set up the new feature. I've tried following the instructions but I'm not sure if I'm doing it right. Could someone help me understand the process better? I don't want to mess anything up.",
        "message_type": "message",
        "priority": "normal",
        "status": "open"
    },
    {
        "ticket_id": "TICKET-003",
        "channel": "social",
        "source": "twitter",
        "customer_id": "CUST-003",
        "customer_email": "happy.customer@example.com",
        "customer_name": "Mike Wilson",
        "subject": "Amazing experience!",
        "content": "Just wanted to say thank you for the incredible support I received today! Your team went above and beyond to help me resolve my issue quickly. I'm so impressed with the level of service and will definitely recommend you to others. Keep up the great work!",
        "message_type": "message",
        "priority": "low",
        "status": "open"
    },
    {
        "ticket_id": "TICKET-004",
        "channel": "phone",
        "source": "call_center",
        "customer_id": "CUST-004",
        "customer_email": "frustrated.user@example.com",
        "customer_name": "Lisa Brown",
        "subject": "Billing issue",
        "content": "I'm really frustrated with the billing situation. I was charged twice this month and when I called customer service, they were not helpful at all. The representative was rude and didn't seem to care about my problem. I need this resolved immediately.",
        "message_type": "message",
        "priority": "high",
        "status": "open"
    },
    {
        "ticket_id": "TICKET-005",
        "channel": "email",
        "source": "zendesk",
        "customer_id": "CUST-005",
        "customer_email": "neutral.user@example.com",
        "customer_name": "David Lee",
        "subject": "Feature request",
        "content": "I would like to request a new feature for the dashboard. It would be helpful to have an export function for the reports. Please let me know if this is something you can implement in the future.",
        "message_type": "message",
        "priority": "normal",
        "status": "open"
    }
]


async def test_health_check(session):
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        async with session.get(f"{API_BASE}/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


async def test_workflow_status(session):
    """Test workflow status endpoint"""
    print("🔍 Testing workflow status...")
    try:
        async with session.get(f"{API_BASE}/health/workflow") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Workflow status: {data}")
                return True
            else:
                print(f"❌ Workflow status failed: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Workflow status error: {e}")
        return False


async def test_detailed_health_check(session):
    """Test detailed health check endpoint"""
    print("🔍 Testing detailed health check...")
    try:
        async with session.get(f"{API_BASE}/health/detailed") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Detailed health check: {data}")
                return True
            else:
                print(f"❌ Detailed health check failed: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Detailed health check error: {e}")
        return False


async def test_create_ticket(session, ticket_data):
    """Test creating a single ticket"""
    print(f"📝 Creating ticket: {ticket_data['ticket_id']}")
    try:
        async with session.post(f"{API_BASE}/tickets/", json=ticket_data) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Ticket created successfully: {data['message']}")
                print(f"   Processing time: {data['processing_metadata']['processing_time_seconds']:.2f}s")
                return data
            else:
                print(f"❌ Failed to create ticket: {response.status}")
                error_text = await response.text()
                print(f"   Error: {error_text}")
                return None
    except Exception as e:
        print(f"❌ Error creating ticket: {e}")
        return None


async def test_bulk_create_tickets(session):
    """Test bulk ticket creation"""
    print("📦 Testing bulk ticket creation...")
    bulk_data = {"tickets": SAMPLE_TICKETS}
    
    try:
        async with session.post(f"{API_BASE}/tickets/bulk", json=bulk_data) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Bulk creation successful: {data['message']}")
                return data
            else:
                print(f"❌ Bulk creation failed: {response.status}")
                return None
    except Exception as e:
        print(f"❌ Error in bulk creation: {e}")
        return None


async def test_get_tickets(session):
    """Test getting tickets"""
    print("📋 Testing get tickets...")
    try:
        async with session.get(f"{API_BASE}/tickets/?size=10") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Retrieved {len(data['tickets'])} tickets (total: {data['total']})")
                return data
            else:
                print(f"❌ Failed to get tickets: {response.status}")
                return None
    except Exception as e:
        print(f"❌ Error getting tickets: {e}")
        return None


async def test_sentiment_analysis(session):
    """Test sentiment analysis endpoint"""
    print("🧠 Testing sentiment analysis...")
    test_content = "I am very angry and frustrated with this terrible service!"
    
    try:
        async with session.post(f"{API_BASE}/sentiment/analyze", json={
            "content": test_content,
            "context": {"test": True}
        }) as response:
            if response.status == 200:
                data = await response.json()
                sentiment = data['sentiment_analysis']
                print(f"✅ Sentiment analysis completed:")
                print(f"   Overall sentiment: {sentiment['overall_sentiment']:.3f}")
                print(f"   Is negative: {sentiment['is_negative']}")
                print(f"   Processing time: {sentiment['processing_time_ms']}ms")
                return data
            else:
                print(f"❌ Sentiment analysis failed: {response.status}")
                return None
    except Exception as e:
        print(f"❌ Error in sentiment analysis: {e}")
        return None


async def test_get_trends(session):
    """Test getting trends"""
    print("📈 Testing trends...")
    try:
        async with session.get(f"{API_BASE}/trends/?time_period=1h") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Trends retrieved successfully")
                return data
            else:
                print(f"❌ Failed to get trends: {response.status}")
                return None
    except Exception as e:
        print(f"❌ Error getting trends: {e}")
        return None


async def test_get_alerts(session):
    """Test getting alerts"""
    print("🚨 Testing alerts...")
    try:
        async with session.get(f"{API_BASE}/alerts/?active_only=true&size=10") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Retrieved {len(data['alerts'])} alerts (total: {data['total']})")
                return data
            else:
                print(f"❌ Failed to get alerts: {response.status}")
                return None
    except Exception as e:
        print(f"❌ Error getting alerts: {e}")
        return None


async def run_performance_test(session, num_tickets=10):
    """Run performance test with multiple tickets"""
    print(f"⚡ Running performance test with {num_tickets} tickets...")
    
    start_time = datetime.now()
    results = []
    
    for i in range(num_tickets):
        ticket_data = SAMPLE_TICKETS[i % len(SAMPLE_TICKETS)].copy()
        ticket_data["ticket_id"] = f"PERF-{i:03d}"
        ticket_data["customer_email"] = f"test{i}@example.com"
        
        result = await test_create_ticket(session, ticket_data)
        if result:
            results.append(result)
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    avg_time = total_time / len(results) if results else 0
    
    print(f"📊 Performance test results:")
    print(f"   Total tickets processed: {len(results)}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average time per ticket: {avg_time:.2f}s")
    print(f"   Tickets per second: {len(results)/total_time:.2f}")


async def main():
    """Main test function"""
    print("🚀 Starting Customer Sentiment Watchdog API Tests")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test health check
        if not await test_health_check(session):
            print("❌ Health check failed, stopping tests")
            return
        
        print("\n" + "=" * 50)
        
        # Test workflow status
        await test_workflow_status(session)
        await test_detailed_health_check(session)
        
        print("\n" + "=" * 50)
        
        # Test individual ticket creation
        print("Testing individual ticket creation...")
        for ticket in SAMPLE_TICKETS[:2]:  # Test first 2 tickets
            await test_create_ticket(session, ticket)
            await asyncio.sleep(1)  # Small delay between requests
        
        print("\n" + "=" * 50)
        
        # Test bulk creation
        await test_bulk_create_tickets(session)
        
        print("\n" + "=" * 50)
        
        # Test other endpoints
        await test_get_tickets(session)
        await test_sentiment_analysis(session)
        await test_get_trends(session)
        await test_get_alerts(session)
        
        print("\n" + "=" * 50)
        
        # Performance test
        await run_performance_test(session, num_tickets=5)
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
