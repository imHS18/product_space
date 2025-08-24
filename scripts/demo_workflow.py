#!/usr/bin/env python3
"""
Demo script for the Customer Sentiment Watchdog Workflow
Shows how to use the workflow system directly without the API
"""

import asyncio
import json
from datetime import datetime
from workflows.agent_crew import create_sentiment_workflow


async def demo_workflow():
    """Demonstrate the workflow system in action"""
    
    print("🚀 Customer Sentiment Watchdog Workflow Demo")
    print("=" * 60)
    
    # Configuration (you can set these via environment variables)
    config = {
        'GOOGLE_GEMINI_API_KEY': None,  # Set your key here or via env var
        'SLACK_WEBHOOK_URL': None,      # Set your webhook here or via env var
        'DATABASE_URL': 'sqlite+aiosqlite:///sentiment_watchdog.db',
        'SENTIMENT_ANALYSIS_ENABLED': True,
        'ALERT_THRESHOLD': 0.3,
        'SLACK_COOLDOWN_MINUTES': 15,
        'MAX_PROCESSING_TIME': 5
    }
    
    try:
        # Create and initialize the workflow
        print("🔧 Initializing workflow system...")
        workflow = create_sentiment_workflow(config)
        
        # Get initial status
        print("\n📊 Workflow Status:")
        status = await workflow.get_workflow_status()
        print(json.dumps(status, indent=2))
        
        # Sample tickets for demonstration
        sample_tickets = [
            {
                'id': 'DEMO-001',
                'content': 'I am extremely frustrated with your service! This is the third time I have this issue and nobody is helping me. I want to speak to a manager immediately!',
                'customer_id': 'angry.customer@example.com',
                'channel': 'email',
                'source': 'zendesk',
                'priority': 'urgent',
                'metadata': {
                    'customer_tier': 'premium',
                    'account_value': 5000,
                    'tags': ['billing', 'urgent']
                }
            },
            {
                'id': 'DEMO-002',
                'content': 'Hi there! I just wanted to say thank you for the amazing support I received today. Your team went above and beyond to help me resolve my issue quickly. I\'m so impressed!',
                'customer_id': 'happy.customer@example.com',
                'channel': 'chat',
                'source': 'intercom',
                'priority': 'low',
                'metadata': {
                    'customer_tier': 'standard',
                    'account_value': 1000,
                    'tags': ['positive', 'feedback']
                }
            },
            {
                'id': 'DEMO-003',
                'content': 'I\'m a bit confused about how to set up the new feature. I\'ve tried following the instructions but I\'m not sure if I\'m doing it right. Could someone help me understand?',
                'customer_id': 'confused.user@example.com',
                'channel': 'email',
                'source': 'zendesk',
                'priority': 'normal',
                'metadata': {
                    'customer_tier': 'standard',
                    'account_value': 500,
                    'tags': ['setup', 'help']
                }
            }
        ]
        
        # Process each ticket through the workflow
        for i, ticket in enumerate(sample_tickets, 1):
            print(f"\n{'='*60}")
            print(f"🎯 Processing Ticket {i}: {ticket['id']}")
            print(f"Customer: {ticket['customer_id']}")
            print(f"Priority: {ticket['priority']}")
            print(f"Content: {ticket['content'][:100]}...")
            
            start_time = datetime.now()
            
            # Process the ticket
            result = await workflow.process_ticket(ticket)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            print(f"\n⏱️  Processing Time: {processing_time:.2f} seconds")
            print(f"📋 Workflow Status: {result.get('workflow_status', 'unknown')}")
            print(f"🤖 Agents Used: {', '.join(result.get('agents_used', []))}")
            
            # Show workflow output summary
            workflow_output = result.get('result', {})
            if isinstance(workflow_output, str):
                print(f"\n📄 Workflow Output (preview):")
                print(workflow_output[:200] + "..." if len(workflow_output) > 200 else workflow_output)
            else:
                print(f"\n📄 Workflow Output Keys: {list(workflow_output.keys()) if isinstance(workflow_output, dict) else 'Not a dict'}")
        
        # Test bulk processing
        print(f"\n{'='*60}")
        print("🚀 Testing Bulk Processing...")
        
        bulk_start = datetime.now()
        bulk_results = await workflow.process_bulk_tickets(sample_tickets)
        bulk_end = datetime.now()
        bulk_time = (bulk_end - bulk_start).total_seconds()
        
        print(f"⏱️  Bulk Processing Time: {bulk_time:.2f} seconds")
        print(f"📊 Processed {len(bulk_results)} tickets")
        print(f"📈 Average time per ticket: {bulk_time/len(bulk_results):.2f} seconds")
        
        # Final status check
        print(f"\n{'='*60}")
        print("📊 Final Workflow Status:")
        final_status = await workflow.get_workflow_status()
        print(json.dumps(final_status, indent=2))
        
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        await workflow.cleanup()
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


async def demo_workflow_status():
    """Demonstrate workflow status monitoring"""
    
    print("\n🔍 Workflow Status Monitoring Demo")
    print("=" * 40)
    
    config = {
        'GOOGLE_GEMINI_API_KEY': None,
        'SLACK_WEBHOOK_URL': None,
        'DATABASE_URL': 'sqlite+aiosqlite:///sentiment_watchdog.db'
    }
    
    try:
        workflow = create_sentiment_workflow(config)
        
        # Check status before processing
        print("📊 Status before processing:")
        status = await workflow.get_workflow_status()
        print(f"   Workflow Status: {status.get('workflow_status', 'unknown')}")
        print(f"   Agents Count: {status.get('agents_count', 0)}")
        print(f"   Tools Count: {status.get('tools_count', 0)}")
        
        # Process a simple ticket
        test_ticket = {
            'id': 'STATUS-TEST',
            'content': 'This is a test ticket for status monitoring.',
            'customer_id': 'test@example.com',
            'channel': 'test',
            'source': 'demo',
            'priority': 'low'
        }
        
        print("\n🔄 Processing test ticket...")
        result = await workflow.process_ticket(test_ticket)
        
        # Check status after processing
        print("\n📊 Status after processing:")
        status = await workflow.get_workflow_status()
        print(f"   Workflow Status: {status.get('workflow_status', 'unknown')}")
        print(f"   Crew Status: {status.get('crew_status', 'unknown')}")
        
        await workflow.cleanup()
        print("✅ Status monitoring demo completed!")
        
    except Exception as e:
        print(f"❌ Error in status demo: {e}")


if __name__ == "__main__":
    print("🎬 Starting Customer Sentiment Watchdog Workflow Demos")
    
    # Run the main demo
    asyncio.run(demo_workflow())
    
    # Run the status monitoring demo
    asyncio.run(demo_workflow_status())
    
    print("\n🎉 All demos completed!")
