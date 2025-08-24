import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_slack_webhook():
    """Test Slack webhook directly"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL not found in environment variables")
        return
    
    print(f"🔗 Testing Slack webhook: {webhook_url[:50]}...")
    
    # Test message
    test_message = {
        "text": "🚨 *TEST ALERT* - Sentiment Watchdog System",
        "attachments": [
            {
                "color": "#FF0000",
                "fields": [
                    {
                        "title": "Test Type",
                        "value": "Direct Webhook Test",
                        "short": True
                    },
                    {
                        "title": "Status",
                        "value": "Testing",
                        "short": True
                    },
                    {
                        "title": "Message",
                        "value": "This is a test message from the Sentiment Watchdog system to verify Slack integration is working.",
                        "short": False
                    }
                ],
                "footer": "Sentiment Watchdog Test",
                "ts": 1234567890
            }
        ]
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                webhook_url,
                json=test_message,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"📡 Response Status: {response.status}")
                
                if response.status == 200:
                    print("✅ Slack notification sent successfully!")
                    response_text = await response.text()
                    print(f"📄 Response: {response_text}")
                else:
                    print(f"❌ Slack notification failed with status {response.status}")
                    response_text = await response.text()
                    print(f"📄 Error Response: {response_text}")
                    
    except Exception as e:
        print(f"❌ Error testing Slack webhook: {e}")

if __name__ == "__main__":
    asyncio.run(test_slack_webhook())
