"""
Alert Manager Agent for detecting and managing sentiment alerts
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.services.slack_service import SlackService

logger = logging.getLogger(__name__)


class AlertManagerAgent:
    """AI Agent for managing sentiment alerts and notifications"""
    
    def __init__(self):
        self.slack_service = None
        self._initialized = False
        self._alert_cooldown = {}  # Track recent alerts to prevent spam
    
    async def initialize(self):
        """Initialize alert manager"""
        if self._initialized:
            return
        
        logger.info("🚨 Initializing Alert Manager Agent...")
        
        try:
            # Initialize Slack service if webhook URL is configured
            if settings.SLACK_WEBHOOK_URL:
                self.slack_service = SlackService()
                await self.slack_service.initialize()
            
            self._initialized = True
            logger.info("✅ Alert Manager Agent initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize alert manager: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup agent resources"""
        if self.slack_service:
            await self.slack_service.cleanup()
        self._initialized = False
        logger.info("🧹 Alert Manager Agent cleaned up")
    
    async def check_alerts(self, sentiment_result: Dict[str, Any], ticket_data: Any) -> Dict[str, Any]:
        """
        Check if sentiment analysis results warrant an alert
        
        Args:
            sentiment_result: Results from sentiment analysis
            ticket_data: Original ticket data
            
        Returns:
            Dict containing alert decision and details
        """
        if not self._initialized:
            raise RuntimeError("Alert manager not initialized")
        
        try:
            # Check if we should alert based on sentiment
            should_alert = self._should_trigger_alert(sentiment_result, ticket_data)
            
            if not should_alert:
                return {
                    "should_alert": False,
                    "reason": "No alert conditions met"
                }
            
            # Check cooldown to prevent spam
            cooldown_key = f"{ticket_data.channel}_{ticket_data.source}"
            if self._is_in_cooldown(cooldown_key):
                return {
                    "should_alert": False,
                    "reason": "Alert in cooldown period"
                }
            
            # Determine alert severity
            severity = self._determine_severity(sentiment_result, ticket_data)
            
            # Generate alert content
            alert_content = self._generate_alert_content(sentiment_result, ticket_data, severity)
            
            # Send alert if configured
            alert_sent = False
            if self.slack_service:
                try:
                    await self.slack_service.send_alert(alert_content)
                    alert_sent = True
                    logger.info(f"🚨 Alert sent for ticket {ticket_data.ticket_id}")
                except Exception as e:
                    logger.error(f"Failed to send Slack alert: {e}")
            
            # Update cooldown
            self._update_cooldown(cooldown_key)
            
            return {
                "should_alert": True,
                "severity": severity,
                "alert_type": "negative_sentiment",
                "title": alert_content["title"],
                "message": alert_content["message"],
                "recommendations": alert_content.get("recommendations"),
                "sent_to_slack": alert_sent,
                "threshold_breached": sentiment_result["overall_sentiment"],
                "alert_data": {
                    "ticket_id": ticket_data.ticket_id,
                    "customer_email": ticket_data.customer_email,
                    "channel": ticket_data.channel,
                    "source": ticket_data.source,
                    "sentiment_scores": {
                        "overall": sentiment_result["overall_sentiment"],
                        "anger": sentiment_result.get("anger_score", 0.0),
                        "frustration": sentiment_result.get("frustration_score", 0.0)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error in alert check: {e}")
            raise
    
    def _should_trigger_alert(self, sentiment_result: Dict[str, Any], ticket_data: Any) -> bool:
        """Determine if an alert should be triggered"""
        # Check negative sentiment threshold
        if sentiment_result["overall_sentiment"] < -settings.SENTIMENT_THRESHOLD:
            return True
        
        # Check high emotion scores
        if (sentiment_result.get("anger_score", 0.0) > 0.5 or 
            sentiment_result.get("frustration_score", 0.0) > 0.5):
            return True
        
        # Check high priority tickets
        if ticket_data.priority in ["high", "urgent"]:
            return True
        
        return False
    
    def _determine_severity(self, sentiment_result: Dict[str, Any], ticket_data: Any) -> str:
        """Determine alert severity level"""
        sentiment_score = abs(sentiment_result["overall_sentiment"])
        anger_score = sentiment_result.get("anger_score", 0.0)
        frustration_score = sentiment_result.get("frustration_score", 0.0)
        
        # Critical conditions
        if (sentiment_score > 0.7 or anger_score > 0.7 or 
            ticket_data.priority == "urgent"):
            return "critical"
        
        # High conditions
        if (sentiment_score > 0.5 or anger_score > 0.5 or 
            frustration_score > 0.5 or ticket_data.priority == "high"):
            return "high"
        
        # Medium conditions
        if sentiment_score > 0.3:
            return "medium"
        
        return "low"
    
    def _generate_alert_content(self, sentiment_result: Dict[str, Any], ticket_data: Any, severity: str) -> Dict[str, str]:
        """Generate alert content for notifications"""
        sentiment_score = sentiment_result["overall_sentiment"]
        
        # Generate title
        if severity == "critical":
            title = f"🚨 CRITICAL: Very Negative Customer Sentiment Detected"
        elif severity == "high":
            title = f"⚠️ HIGH: Negative Customer Sentiment Alert"
        else:
            title = f"📊 MEDIUM: Customer Sentiment Alert"
        
        # Generate message
        message = f"""
*Customer Sentiment Alert*

**Ticket:** {ticket_data.ticket_id}
**Customer:** {ticket_data.customer_name or ticket_data.customer_email or 'Unknown'}
**Channel:** {ticket_data.channel.title()}
**Source:** {ticket_data.source.title()}
**Priority:** {ticket_data.priority.title()}

**Sentiment Analysis:**
• Overall Sentiment: {sentiment_score:.3f} ({self._get_sentiment_label(sentiment_score)})
• Anger Score: {sentiment_result.get('anger_score', 0.0):.3f}
• Frustration Score: {sentiment_result.get('frustration_score', 0.0):.3f}

**Content Preview:** {ticket_data.content[:200]}{'...' if len(ticket_data.content) > 200 else ''}
        """.strip()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(sentiment_result, ticket_data, severity)
        
        return {
            "title": title,
            "message": message,
            "recommendations": recommendations
        }
    
    def _get_sentiment_label(self, score: float) -> str:
        """Get human-readable sentiment label"""
        if score < -0.5:
            return "Very Negative"
        elif score < -0.1:
            return "Negative"
        elif score < 0.1:
            return "Neutral"
        elif score < 0.5:
            return "Positive"
        else:
            return "Very Positive"
    
    def _generate_recommendations(self, sentiment_result: Dict[str, Any], ticket_data: Any, severity: str) -> str:
        """Generate response recommendations"""
        recommendations = []
        
        if severity in ["critical", "high"]:
            recommendations.append("• **Immediate attention required** - Consider escalating to senior support")
            recommendations.append("• **Personal outreach** - Phone call or direct message recommended")
        
        if sentiment_result.get("anger_score", 0.0) > 0.3:
            recommendations.append("• **High anger detected** - Use calming language and acknowledge frustration")
        
        if sentiment_result.get("confusion_score", 0.0) > 0.3:
            recommendations.append("• **Customer confusion detected** - Provide clear, step-by-step explanations")
        
        if ticket_data.priority in ["high", "urgent"]:
            recommendations.append("• **High priority ticket** - Expedite resolution process")
        
        if not recommendations:
            recommendations.append("• **Standard response** - Follow normal support procedures")
        
        return "\n".join(recommendations)
    
    def _is_in_cooldown(self, cooldown_key: str) -> bool:
        """Check if alert is in cooldown period"""
        if cooldown_key not in self._alert_cooldown:
            return False
        
        cooldown_time = self._alert_cooldown[cooldown_key]
        return datetime.now() < cooldown_time
    
    def _update_cooldown(self, cooldown_key: str):
        """Update cooldown timestamp"""
        cooldown_duration = timedelta(minutes=settings.ALERT_COOLDOWN_MINUTES)
        self._alert_cooldown[cooldown_key] = datetime.now() + cooldown_duration
