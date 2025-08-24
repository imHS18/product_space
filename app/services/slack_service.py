"""
Slack Service for sending alerts and notifications
"""

import logging
import aiohttp
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class SlackService:
    """Service for sending alerts to Slack"""
    
    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL
        self.channel = settings.SLACK_CHANNEL
        self._initialized = False
    
    async def initialize(self):
        """Initialize Slack service"""
        if self._initialized:
            return
        
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured - alerts will not be sent")
            return
        
        logger.info("📱 Initializing Slack Service...")
        self._initialized = True
        logger.info("✅ Slack Service initialized")
    
    async def cleanup(self):
        """Cleanup service resources"""
        self._initialized = False
        logger.info("🧹 Slack Service cleaned up")
    
    async def send_alert(self, alert_content: Dict[str, str]) -> bool:
        """
        Send alert to Slack
        
        Args:
            alert_content: Dict containing title, message, and recommendations
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self._initialized or not self.webhook_url:
            logger.warning("Slack service not initialized or webhook not configured")
            return False
        
        try:
            # Prepare Slack message
            slack_message = self._format_slack_message(alert_content)
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=slack_message,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Slack alert sent successfully")
                        return True
                    else:
                        logger.error(f"Failed to send Slack alert: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return False
    
    def _format_slack_message(self, alert_content: Dict[str, str]) -> Dict[str, Any]:
        """Format alert content for Slack message"""
        # Create Slack message structure
        message = {
            "channel": self.channel,
            "text": alert_content["title"],
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": alert_content["title"]
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": alert_content["message"]
                    }
                }
            ]
        }
        
        # Add recommendations if available
        if alert_content.get("recommendations"):
            message["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recommendations:*\n{alert_content['recommendations']}"
                }
            })
        
        # Add divider
        message["blocks"].append({
            "type": "divider"
        })
        
        return message
    
    async def send_test_message(self) -> bool:
        """Send a test message to verify Slack integration"""
        test_content = {
            "title": "🧪 Test Alert - Sentiment Watchdog",
            "message": "This is a test message to verify Slack integration is working correctly.",
            "recommendations": "• Test completed successfully\n• Integration is operational"
        }
        
        return await self.send_alert(test_content)
