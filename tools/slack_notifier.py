"""
Slack Notifier Tool
Sends formatted alerts and notifications to Slack channels
"""

import logging
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from crewai.tools import BaseTool
from app.core.config import settings

logger = logging.getLogger(__name__)


class SlackNotifier(BaseTool):
    """Tool for sending formatted alerts and notifications to Slack channels"""
    
    name: str = "Slack Notifier"
    description: str = "Sends formatted alerts and notifications to Slack channels for sentiment alerts, system status, and team communications."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'webhook_url', settings.SLACK_WEBHOOK_URL)
        object.__setattr__(self, 'notification_history', [])
        object.__setattr__(self, 'cooldown_period', timedelta(minutes=settings.SLACK_COOLDOWN_MINUTES))
        object.__setattr__(self, 'last_notification_time', None)
    
    def _run(self, message: str, channel: str = "#customer-support-alerts") -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        print(f"🔔 SLACK NOTIFIER CALLED: message='{message}', channel='{channel}'")
        print(f"🔔 Webhook URL configured: {bool(self.webhook_url)}")
        
        try:
            # Parse the message to extract sentiment data
            # Look for sentiment score in the message
            import re
            sentiment_score = 0.0
            risk_level = "LOW"
            customer_tier = "Standard"
            
            # Try to extract sentiment score from the message
            sentiment_match = re.search(r"sentiment.*?([-\d.]+)", message.lower())
            if sentiment_match:
                try:
                    sentiment_score = float(sentiment_match.group(1))
                except:
                    sentiment_score = 0.0
            
            # Determine risk level based on sentiment
            if sentiment_score < -0.5:
                risk_level = "HIGH"
                color = "#FF0000"  # Red
                emoji = "😠"
            elif sentiment_score < -0.2:
                risk_level = "MEDIUM"
                color = "#FFA500"  # Orange
                emoji = "😐"
            else:
                risk_level = "LOW"
                color = "#00FF00"  # Green
                emoji = "😊"
            
            # Create a rich formatted message like the image
            test_message = {
                "text": f"🚨 *Sentiment Alert*",
                "attachments": [
                    {
                        "color": color,
                        "blocks": [
                            {
                                "type": "header",
                                "text": {
                                    "type": "plain_text",
                                    "text": f"🚨 Sentiment Alert - {channel}",
                                    "emoji": True
                                }
                            },
                            {
                                "type": "section",
                                "fields": [
                                    {
                                        "type": "mrkdwn",
                                        "text": f"*Sentiment Score:*\n{emoji} {sentiment_score:.2f}"
                                    },
                                    {
                                        "type": "mrkdwn",
                                        "text": f"*Risk Level:*\n🔴 {risk_level}"
                                    }
                                ]
                            },
                            {
                                "type": "section",
                                "fields": [
                                    {
                                        "type": "mrkdwn",
                                        "text": f"*Customer Tier:*\n👤 {customer_tier}"
                                    },
                                    {
                                        "type": "mrkdwn",
                                        "text": f"*Timestamp:*\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                    }
                                ]
                            },
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"*Alert Details:*\n{message}"
                                }
                            },
                            {
                                "type": "actions",
                                "elements": [
                                    {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "Acknowledge",
                                            "emoji": True
                                        },
                                        "style": "primary",
                                        "action_id": "acknowledge_alert"
                                    },
                                    {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "View Details",
                                            "emoji": True
                                        },
                                        "action_id": "view_details"
                                    }
                                ]
                            }
                        ],
                        "footer": "Sentiment Watchdog System",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            print(f"🔔 About to send message: {test_message}")
            
            # Use the existing event loop if available, otherwise create a new one
            try:
                # Try to get the current event loop
                loop = asyncio.get_running_loop()
                print(f"🔔 Found running event loop, using ThreadPoolExecutor")
                # If we're in an async context, we need to use a different approach
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._send_sync, test_message)
                    result = future.result(timeout=10)
            except RuntimeError:
                print(f"🔔 No event loop running, creating new one")
                # No event loop running, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self._send_to_slack(test_message))
                finally:
                    loop.close()
            
            print(f"🔔 Slack send result: {result}")
            
            if result["success"]:
                print(f"✅ SLACK NOTIFICATION SENT SUCCESSFULLY!")
                return f"✅ Slack notification sent successfully to {channel}: {message}"
            else:
                print(f"❌ SLACK NOTIFICATION FAILED: {result.get('error', 'Unknown error')}")
                return f"❌ Slack notification failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            print(f"❌ SLACK NOTIFIER ERROR: {e}")
            logger.error(f"Error in Slack notifier _run: {e}")
            return f"❌ Error sending Slack notification: {str(e)}"
    
    def _send_sync(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of _send_to_slack for use in threads"""
        import aiohttp
        import asyncio
        
        async def _send():
            return await self._send_to_slack(message)
        
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_send())
        finally:
            loop.close()
    
    async def send_notification(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send notification to Slack
        
        Args:
            message_data: Dictionary containing notification details
            
        Returns:
            Dictionary with notification status
        """
        try:
            # Check cooldown
            if not self._can_send_notification():
                return {
                    "success": False,
                    "error": "Cooldown period active",
                    "next_available": self._get_next_available_time()
                }
            
            # Format message
            formatted_message = self._format_slack_message(message_data)
            
            # Send to Slack
            result = await self._send_to_slack(formatted_message)
            
            if result["success"]:
                # Update notification history
                self._record_notification(message_data, result)
                object.__setattr__(self, 'last_notification_time', datetime.now())
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_sentiment_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send sentiment alert to Slack"""
        try:
            # Create alert message
            alert_message = {
                "type": "sentiment_alert",
                "severity": alert_data.get("severity", "medium"),
                "customer_email": alert_data.get("customer_email", "unknown"),
                "sentiment_score": alert_data.get("sentiment_score", 0.0),
                "risk_level": alert_data.get("risk_level", "unknown"),
                "ticket_id": alert_data.get("ticket_id", "unknown"),
                "message": alert_data.get("message", "Sentiment alert triggered"),
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.send_notification(alert_message)
            
        except Exception as e:
            logger.error(f"Error sending sentiment alert: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_system_status(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send system status update to Slack"""
        try:
            # Create status message
            status_message = {
                "type": "system_status",
                "status": status_data.get("status", "unknown"),
                "health_score": status_data.get("health_score", 0.0),
                "active_tickets": status_data.get("active_tickets", 0),
                "alerts_triggered": status_data.get("alerts_triggered", 0),
                "response_time_avg": status_data.get("response_time_avg", 0.0),
                "message": status_data.get("message", "System status update"),
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.send_notification(status_message)
            
        except Exception as e:
            logger.error(f"Error sending system status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_team_alert(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send team-specific alert to Slack"""
        try:
            # Create team alert message
            team_message = {
                "type": "team_alert",
                "team": team_data.get("team", "unknown"),
                "alert_type": team_data.get("alert_type", "general"),
                "priority": team_data.get("priority", "medium"),
                "assignee": team_data.get("assignee", "unassigned"),
                "customer_tier": team_data.get("customer_tier", "standard"),
                "message": team_data.get("message", "Team alert"),
                "timestamp": datetime.now().isoformat()
            }
            
            return await self.send_notification(team_message)
            
        except Exception as e:
            logger.error(f"Error sending team alert: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _can_send_notification(self) -> bool:
        """Check if notification can be sent (cooldown check)"""
        if not self.last_notification_time:
            return True
        
        time_since_last = datetime.now() - self.last_notification_time
        return time_since_last >= self.cooldown_period
    
    def _get_next_available_time(self) -> str:
        """Get next available time for notification"""
        if not self.last_notification_time:
            return datetime.now().isoformat()
        
        next_time = self.last_notification_time + self.cooldown_period
        return next_time.isoformat()
    
    def _format_slack_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format message for Slack API"""
        message_type = message_data.get("type", "general")
        
        if message_type == "sentiment_alert":
            return self._format_sentiment_alert(message_data)
        elif message_type == "system_status":
            return self._format_system_status(message_data)
        elif message_type == "team_alert":
            return self._format_team_alert(message_data)
        else:
            return self._format_general_message(message_data)
    
    def _format_sentiment_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format sentiment alert for Slack"""
        severity = alert_data.get("severity", "medium")
        sentiment_score = alert_data.get("sentiment_score", 0.0)
        risk_level = alert_data.get("risk_level", "unknown")
        
        # Determine color based on severity
        color_map = {
            "critical": "#FF0000",  # Red
            "high": "#FF6B35",      # Orange
            "medium": "#FFA500",    # Orange
            "low": "#FFD700"        # Yellow
        }
        color = color_map.get(severity, "#808080")  # Gray default
        
        # Determine emoji based on sentiment
        if sentiment_score < -0.5:
            emoji = "😠"
        elif sentiment_score < -0.2:
            emoji = "😐"
        else:
            emoji = "😊"
        
        return {
            "text": f"{emoji} *Sentiment Alert*",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Customer",
                            "value": alert_data.get("customer_email", "Unknown"),
                            "short": True
                        },
                        {
                            "title": "Sentiment Score",
                            "value": f"{sentiment_score:.2f}",
                            "short": True
                        },
                        {
                            "title": "Risk Level",
                            "value": risk_level.upper(),
                            "short": True
                        },
                        {
                            "title": "Ticket ID",
                            "value": alert_data.get("ticket_id", "Unknown"),
                            "short": True
                        },
                        {
                            "title": "Message",
                            "value": alert_data.get("message", "Sentiment alert triggered"),
                            "short": False
                        }
                    ],
                    "footer": "Sentiment Watchdog",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
    
    def _format_system_status(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format system status for Slack"""
        status = status_data.get("status", "unknown")
        health_score = status_data.get("health_score", 0.0)
        
        # Determine color based on health score
        if health_score >= 0.8:
            color = "#00FF00"  # Green
            emoji = "✅"
        elif health_score >= 0.6:
            color = "#FFD700"  # Yellow
            emoji = "⚠️"
        else:
            color = "#FF0000"  # Red
            emoji = "🚨"
        
        return {
            "text": f"{emoji} *System Status Update*",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Status",
                            "value": status.upper(),
                            "short": True
                        },
                        {
                            "title": "Health Score",
                            "value": f"{health_score:.2f}",
                            "short": True
                        },
                        {
                            "title": "Active Tickets",
                            "value": str(status_data.get("active_tickets", 0)),
                            "short": True
                        },
                        {
                            "title": "Alerts Triggered",
                            "value": str(status_data.get("alerts_triggered", 0)),
                            "short": True
                        },
                        {
                            "title": "Avg Response Time",
                            "value": f"{status_data.get('response_time_avg', 0.0):.2f}s",
                            "short": True
                        },
                        {
                            "title": "Message",
                            "value": status_data.get("message", "System status update"),
                            "short": False
                        }
                    ],
                    "footer": "Sentiment Watchdog",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
    
    def _format_team_alert(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format team alert for Slack"""
        priority = team_data.get("priority", "medium")
        team = team_data.get("team", "unknown")
        
        # Determine color based on priority
        color_map = {
            "critical": "#FF0000",  # Red
            "high": "#FF6B35",      # Orange
            "medium": "#FFA500",    # Orange
            "low": "#FFD700"        # Yellow
        }
        color = color_map.get(priority, "#808080")  # Gray default
        
        # Determine emoji based on priority
        emoji_map = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "📢",
            "low": "ℹ️"
        }
        emoji = emoji_map.get(priority, "📢")
        
        return {
            "text": f"{emoji} *Team Alert*",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Team",
                            "value": team.upper(),
                            "short": True
                        },
                        {
                            "title": "Priority",
                            "value": priority.upper(),
                            "short": True
                        },
                        {
                            "title": "Assignee",
                            "value": team_data.get("assignee", "Unassigned"),
                            "short": True
                        },
                        {
                            "title": "Customer Tier",
                            "value": team_data.get("customer_tier", "Standard").title(),
                            "short": True
                        },
                        {
                            "title": "Alert Type",
                            "value": team_data.get("alert_type", "General").title(),
                            "short": True
                        },
                        {
                            "title": "Message",
                            "value": team_data.get("message", "Team alert"),
                            "short": False
                        }
                    ],
                    "footer": "Sentiment Watchdog",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
    
    def _format_general_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format general message for Slack"""
        return {
            "text": f"📢 *{message_data.get('title', 'Notification')}*",
            "attachments": [
                {
                    "color": "#36A2EB",  # Blue
                    "text": message_data.get("message", "General notification"),
                    "footer": "Sentiment Watchdog",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
    
    async def _send_to_slack(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to Slack webhook"""
        print(f"🔔 _send_to_slack called with message: {message}")
        print(f"🔔 Webhook URL: {self.webhook_url}")
        
        try:
            if not self.webhook_url:
                print(f"❌ No webhook URL configured!")
                return {
                    "success": False,
                    "error": "Slack webhook URL not configured"
                }
            
            print(f"🔔 Sending HTTP POST to Slack webhook...")
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.webhook_url,
                    json=message,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    print(f"🔔 HTTP Response Status: {response.status}")
                    print(f"🔔 HTTP Response Headers: {dict(response.headers)}")
                    
                    response_text = await response.text()
                    print(f"🔔 HTTP Response Body: {response_text}")
                    
                    if response.status == 200:
                        print(f"✅ HTTP 200 - Slack notification sent successfully!")
                        logger.info("Slack notification sent successfully")
                        return {
                            "success": True,
                            "status_code": response.status,
                            "message": "Notification sent successfully"
                        }
                    else:
                        print(f"❌ HTTP {response.status} - Slack notification failed!")
                        logger.warning(f"Slack notification failed with status {response.status}")
                        return {
                            "success": False,
                            "status_code": response.status,
                            "error": f"HTTP {response.status}: {response_text}"
                        }
                        
        except asyncio.TimeoutError:
            print(f"❌ Slack notification timeout!")
            logger.error("Slack notification timeout")
            return {
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            print(f"❌ Error sending to Slack: {e}")
            logger.error(f"Error sending to Slack: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _record_notification(self, message_data: Dict[str, Any], result: Dict[str, Any]):
        """Record notification in history"""
        notification_record = {
            "timestamp": datetime.now(),
            "type": message_data.get("type", "general"),
            "success": result.get("success", False),
            "status_code": result.get("status_code"),
            "error": result.get("error")
        }
        
        self.notification_history.append(notification_record)
        
        # Keep only last 100 notifications
        if len(self.notification_history) > 100:
            self.notification_history.pop(0)
    
    def get_notification_status(self) -> Dict[str, Any]:
        """Get notification system status"""
        return {
            "webhook_configured": bool(self.webhook_url),
            "cooldown_period_minutes": self.cooldown_period.total_seconds() / 60,
            "last_notification_time": self.last_notification_time.isoformat() if self.last_notification_time else None,
            "can_send_now": self._can_send_notification(),
            "total_notifications_sent": len([n for n in self.notification_history if n["success"]]),
            "total_notifications_failed": len([n for n in self.notification_history if not n["success"]])
        }
    
    def get_recent_notifications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent notification history"""
        recent = self.notification_history[-limit:] if self.notification_history else []
        
        return [
            {
                "timestamp": record["timestamp"].isoformat(),
                "type": record["type"],
                "success": record["success"],
                "status_code": record["status_code"],
                "error": record["error"]
            }
            for record in recent
        ]
    
    def update_cooldown_period(self, minutes: int):
        """Update cooldown period"""
        object.__setattr__(self, 'cooldown_period', timedelta(minutes=minutes))
        logger.info(f"Updated cooldown period to {minutes} minutes")
    
    def reset_cooldown(self):
        """Reset cooldown (for testing or emergency)"""
        object.__setattr__(self, 'last_notification_time', None)
        logger.info("Cooldown reset")
