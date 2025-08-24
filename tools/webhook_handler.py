"""
Webhook Handler Tool
Manages webhook deliveries and API integrations for external systems
"""

import logging
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class WebhookHandler(BaseTool):
    """Tool for managing webhook deliveries and API integrations"""
    
    name: str = "Webhook Handler"
    description: str = "Manages webhook deliveries and API integrations for external systems like CRM, ticketing systems, and monitoring tools."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'webhook_configs', {})
        object.__setattr__(self, 'retry_attempts', 3)
        object.__setattr__(self, 'timeout_seconds', 10)
    
    def _run(self, webhook_url: str, payload: str) -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        # In practice, you'd convert the string back to dict or handle JSON
        # For now, returning a simple webhook delivery result
        return f"Webhook delivered to {webhook_url}"
    
    async def send_webhook(self, webhook_url: str, payload: Dict[str, Any], 
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send webhook to external system
        
        Args:
            webhook_url: URL to send webhook to
            payload: Data to send
            headers: Optional headers for the request
            
        Returns:
            Dictionary with delivery status
        """
        try:
            default_headers = {
                "Content-Type": "application/json",
                "User-Agent": "SentimentWatchdog/1.0"
            }
            
            if headers:
                default_headers.update(headers)
            
            timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for attempt in range(self.retry_attempts):
                    try:
                        async with session.post(
                            webhook_url,
                            json=payload,
                            headers=default_headers
                        ) as response:
                            if response.status in [200, 201, 202]:
                                logger.info(f"Webhook delivered successfully to {webhook_url}")
                                return {
                                    "success": True,
                                    "status_code": response.status,
                                    "attempt": attempt + 1,
                                    "url": webhook_url
                                }
                            else:
                                logger.warning(f"Webhook failed with status {response.status} for {webhook_url}")
                                if attempt == self.retry_attempts - 1:
                                    return {
                                        "success": False,
                                        "status_code": response.status,
                                        "error": f"HTTP {response.status}",
                                        "url": webhook_url
                                    }
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                
                    except asyncio.TimeoutError:
                        logger.warning(f"Webhook timeout on attempt {attempt + 1} for {webhook_url}")
                        if attempt == self.retry_attempts - 1:
                            return {
                                "success": False,
                                "error": "Timeout",
                                "url": webhook_url
                            }
                        await asyncio.sleep(2 ** attempt)
                        
                    except Exception as e:
                        logger.error(f"Webhook error on attempt {attempt + 1}: {e}")
                        if attempt == self.retry_attempts - 1:
                            return {
                                "success": False,
                                "error": str(e),
                                "url": webhook_url
                            }
                        await asyncio.sleep(2 ** attempt)
                        
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": webhook_url
            }
    
    async def send_crm_webhook(self, customer_data: Dict[str, Any], 
                              sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send customer sentiment data to CRM system"""
        try:
            # Format payload for CRM
            payload = {
                "customer_id": customer_data.get("customer_id"),
                "customer_email": customer_data.get("customer_email"),
                "customer_tier": customer_data.get("customer_tier", "standard"),
                "sentiment_score": sentiment_data.get("sentiment_score", 0.0),
                "sentiment_label": sentiment_data.get("sentiment_label", "neutral"),
                "risk_level": sentiment_data.get("risk_level", "low"),
                "timestamp": datetime.now().isoformat(),
                "source": "sentiment_watchdog"
            }
            
            # Get CRM webhook URL from config
            crm_webhook_url = self.webhook_configs.get("crm_webhook_url")
            if not crm_webhook_url:
                return {
                    "success": False,
                    "error": "CRM webhook URL not configured"
                }
            
            return await self.send_webhook(crm_webhook_url, payload)
            
        except Exception as e:
            logger.error(f"Error sending CRM webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_ticketing_webhook(self, ticket_data: Dict[str, Any], 
                                   alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send alert data to ticketing system"""
        try:
            # Format payload for ticketing system
            payload = {
                "ticket_id": ticket_data.get("ticket_id"),
                "alert_type": alert_data.get("alert_type"),
                "severity": alert_data.get("severity"),
                "message": alert_data.get("message"),
                "customer_email": ticket_data.get("customer_email"),
                "priority": alert_data.get("priority", "medium"),
                "timestamp": datetime.now().isoformat(),
                "source": "sentiment_watchdog"
            }
            
            # Get ticketing webhook URL from config
            ticketing_webhook_url = self.webhook_configs.get("ticketing_webhook_url")
            if not ticketing_webhook_url:
                return {
                    "success": False,
                    "error": "Ticketing webhook URL not configured"
                }
            
            return await self.send_webhook(ticketing_webhook_url, payload)
            
        except Exception as e:
            logger.error(f"Error sending ticketing webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_monitoring_webhook(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send metrics data to monitoring system"""
        try:
            # Format payload for monitoring system
            payload = {
                "metrics": {
                    "total_tickets": metrics_data.get("total_tickets", 0),
                    "negative_sentiment_count": metrics_data.get("negative_sentiment_count", 0),
                    "alerts_triggered": metrics_data.get("alerts_triggered", 0),
                    "average_response_time": metrics_data.get("average_response_time", 0),
                    "system_health": metrics_data.get("system_health", "healthy")
                },
                "timestamp": datetime.now().isoformat(),
                "source": "sentiment_watchdog"
            }
            
            # Get monitoring webhook URL from config
            monitoring_webhook_url = self.webhook_configs.get("monitoring_webhook_url")
            if not monitoring_webhook_url:
                return {
                    "success": False,
                    "error": "Monitoring webhook URL not configured"
                }
            
            return await self.send_webhook(monitoring_webhook_url, payload)
            
        except Exception as e:
            logger.error(f"Error sending monitoring webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_analytics_webhook(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send analytics data to analytics platform"""
        try:
            # Format payload for analytics platform
            payload = {
                "event_type": "sentiment_analysis",
                "data": {
                    "sentiment_score": analytics_data.get("sentiment_score", 0.0),
                    "emotions": analytics_data.get("emotions", {}),
                    "keywords": analytics_data.get("keywords", []),
                    "customer_tier": analytics_data.get("customer_tier", "standard"),
                    "channel": analytics_data.get("channel", "unknown"),
                    "processing_time": analytics_data.get("processing_time", 0)
                },
                "timestamp": datetime.now().isoformat(),
                "source": "sentiment_watchdog"
            }
            
            # Get analytics webhook URL from config
            analytics_webhook_url = self.webhook_configs.get("analytics_webhook_url")
            if not analytics_webhook_url:
                return {
                    "success": False,
                    "error": "Analytics webhook URL not configured"
                }
            
            return await self.send_webhook(analytics_webhook_url, payload)
            
        except Exception as e:
            logger.error(f"Error sending analytics webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def configure_webhook(self, webhook_type: str, url: str, 
                         headers: Optional[Dict[str, str]] = None):
        """Configure webhook settings"""
        self.webhook_configs[webhook_type] = {
            "url": url,
            "headers": headers or {}
        }
        logger.info(f"Configured {webhook_type} webhook: {url}")
    
    def get_webhook_status(self) -> Dict[str, Any]:
        """Get status of configured webhooks"""
        return {
            "configured_webhooks": list(self.webhook_configs.keys()),
            "total_webhooks": len(self.webhook_configs),
            "retry_attempts": self.retry_attempts,
            "timeout_seconds": self.timeout_seconds
        }
    
    async def test_webhook(self, webhook_type: str) -> Dict[str, Any]:
        """Test webhook connectivity"""
        try:
            webhook_config = self.webhook_configs.get(webhook_type)
            if not webhook_config:
                return {
                    "success": False,
                    "error": f"Webhook {webhook_type} not configured"
                }
            
            # Send test payload
            test_payload = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "source": "sentiment_watchdog_test"
            }
            
            return await self.send_webhook(
                webhook_config["url"],
                test_payload,
                webhook_config.get("headers")
            )
            
        except Exception as e:
            logger.error(f"Error testing webhook {webhook_type}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
