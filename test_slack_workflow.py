import asyncio
from tools.slack_notifier import SlackNotifier

async def test_slack_notifier_direct():
    """Test Slack notifier directly"""
    print("🔧 Testing Slack Notifier Tool Directly...")
    
    notifier = SlackNotifier()
    
    # Test the _run method (what CrewAI calls)
    result = notifier._run(
        message="TEST ALERT: This is a direct test of the Slack notifier tool from the workflow",
        channel="#customer-support-alerts"
    )
    
    print(f"📤 Direct Tool Result: {result}")
    
    # Test the async method directly
    test_data = {
        "type": "sentiment_alert",
        "severity": "high",
        "customer_email": "test@example.com",
        "sentiment_score": -0.8,
        "risk_level": "high",
        "ticket_id": "TEST-001",
        "message": "This is a test alert from the async method"
    }
    
    async_result = await notifier.send_sentiment_alert(test_data)
    print(f"📤 Async Method Result: {async_result}")

if __name__ == "__main__":
    asyncio.run(test_slack_notifier_direct())
