"""
Agent Manager for coordinating AI agents in the sentiment analysis system
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.schemas.ticket import TicketCreate, TicketResponse
from app.schemas.sentiment import SentimentAnalysisCreate, SentimentAnalysisResponse
from app.schemas.alert import AlertCreate, AlertResponse

# Import the new workflow
from workflows.agent_crew import SentimentWatchdogWorkflow, create_sentiment_workflow

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages and coordinates all AI agents for sentiment analysis using the workflow system"""
    
    def __init__(self):
        self.workflow: Optional[SentimentWatchdogWorkflow] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the workflow system"""
        if self._initialized:
            return
        
        logger.info("Initializing AI Agent Manager with Workflow...")
        
        try:
            # Create configuration for the workflow
            config = {
                'GOOGLE_GEMINI_API_KEY': settings.GOOGLE_GEMINI_API_KEY,
                'SLACK_WEBHOOK_URL': settings.SLACK_WEBHOOK_URL,
                'DATABASE_URL': settings.DATABASE_URL,
                'SENTIMENT_ANALYSIS_ENABLED': settings.SENTIMENT_ANALYSIS_ENABLED,
                'ALERT_THRESHOLD': settings.ALERT_THRESHOLD,
                'SLACK_COOLDOWN_MINUTES': settings.SLACK_COOLDOWN_MINUTES,
                'MAX_PROCESSING_TIME': settings.MAX_PROCESSING_TIME
            }
            
            # Initialize the workflow
            self.workflow = create_sentiment_workflow(config)
            
            self._initialized = True
            logger.info("Workflow system initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize workflow: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup workflow resources"""
        logger.info("Cleaning up workflow system...")
        
        if self.workflow:
            await self.workflow.cleanup()
        
        self._initialized = False
        logger.info("Workflow cleanup completed")
    
    async def process_ticket(self, ticket_data: TicketCreate) -> Dict[str, Any]:
        """
        Process a ticket through the complete AI agent workflow
        
        Returns:
            Dict containing ticket, sentiment analysis, alerts, and processing metadata
        """
        if not self._initialized:
            raise RuntimeError("Agent manager not initialized")
        
        start_time = datetime.now()
        logger.info(f"🔄 Processing ticket {ticket_data.ticket_id}")
        
        try:
            # Prepare ticket data for workflow
            workflow_ticket_data = {
                'id': ticket_data.ticket_id,
                'content': ticket_data.content,
                'customer_id': ticket_data.customer_email,
                'channel': ticket_data.channel,
                'source': ticket_data.source,
                'priority': ticket_data.priority,
                'created_at': datetime.now().isoformat(),
                'metadata': {
                    'customer_tier': getattr(ticket_data, 'customer_tier', 'standard'),
                    'account_value': getattr(ticket_data, 'account_value', 0),
                    'tags': getattr(ticket_data, 'tags', [])
                }
            }
            
            # Process through workflow
            workflow_result = await self.workflow.process_ticket(workflow_ticket_data)
            
            # Log the workflow result for debugging
            logger.info(f"Workflow result type: {type(workflow_result)}")
            logger.info(f"Workflow result keys: {list(workflow_result.keys()) if isinstance(workflow_result, dict) else 'Not a dict'}")
            
            # Extract results from workflow output
            # The workflow result contains the output from all agents
            result = self._parse_workflow_result(workflow_result, ticket_data)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Add processing metadata
            result['processing_metadata'] = {
                'processing_time_seconds': processing_time,
                'workflow_status': workflow_result.get('workflow_status', 'unknown'),
                'agents_used': workflow_result.get('agents_used', []),
                'processed_at': datetime.now().isoformat()
            }
            
            logger.info(f"Ticket {ticket_data.ticket_id} processed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing ticket {ticket_data.ticket_id}: {e}")
            raise
    
    def _parse_workflow_result(self, workflow_result: Dict[str, Any], original_ticket: TicketCreate) -> Dict[str, Any]:
        """
        Parse the workflow result and extract structured data
        
        Args:
            workflow_result: Raw result from the workflow
            original_ticket: Original ticket data
            
        Returns:
            Structured result with sentiment analysis, alerts, and recommendations
        """
        try:
            # Extract the workflow output
            workflow_output = workflow_result.get('result', {})
            
            # Parse sentiment analysis (from Task 1)
            sentiment_analysis = self._extract_sentiment_analysis(workflow_output)
            
            # Parse alerts (from Task 2)
            alerts = self._extract_alerts(workflow_output)
            
            # Parse response recommendations (from Task 3)
            response_recommendations = self._extract_response_recommendations(workflow_output)
            
            # Parse integration status (from Task 4)
            integration_status = self._extract_integration_status(workflow_output)
            
            return {
                "ticket": original_ticket,
                "sentiment_analysis": sentiment_analysis,
                "alerts": alerts,
                "response_recommendations": response_recommendations,
                "integration_status": integration_status,
                "workflow_output": workflow_output
            }
            
        except Exception as e:
            logger.error(f"Error parsing workflow result: {e}")
            # Return a basic structure if parsing fails
            return {
                "ticket": original_ticket,
                "sentiment_analysis": {"error": "Failed to parse sentiment analysis"},
                "alerts": [],
                "response_recommendations": None,
                "integration_status": {"error": "Failed to parse integration status"},
                "workflow_output": workflow_result
            }
    
    def _extract_sentiment_analysis(self, workflow_output: Any) -> Dict[str, Any]:
        """Extract sentiment analysis from workflow output"""
        try:
            # Convert to string if it's not already
            output_str = str(workflow_output)
            
            # Look for sentiment analysis data in the workflow output string
            # Based on the logs, we know the sentiment analyzer tool produces specific data
            import re
            import json
            
            # Try to extract sentiment data from the workflow output
            # Look for patterns like 'overall_sentiment': -0.744, 'confidence': 0.71, etc.
            
            # Extract overall_sentiment - look for the actual tool output pattern from logs
            sentiment_match = re.search(r"'overall_sentiment':\s*([-\d.]+)", output_str)
            if not sentiment_match:
                sentiment_match = re.search(r"overall_sentiment':\s*([-\d.]+)", output_str)
            if not sentiment_match:
                sentiment_match = re.search(r"overall_sentiment':\s*([-\d.]+)", output_str)
            if not sentiment_match:
                sentiment_match = re.search(r"Sentiment Score:\s*([-\d.]+)", output_str)
            if not sentiment_match:
                # Look for the specific pattern from the tool output
                sentiment_match = re.search(r"overall_sentiment':\s*([-\d.]+)", output_str)
            sentiment_score = float(sentiment_match.group(1)) if sentiment_match else 0.0
            
            # Extract confidence - look for the actual tool output pattern from logs
            confidence_match = re.search(r"'confidence':\s*([\d.]+)", output_str)
            if not confidence_match:
                confidence_match = re.search(r"confidence':\s*([\d.]+)", output_str)
            if not confidence_match:
                confidence_match = re.search(r"Confidence:\s*([\d.]+)", output_str)
            if not confidence_match:
                # Look for the specific pattern from the tool output
                confidence_match = re.search(r"confidence':\s*([\d.]+)", output_str)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            
            # Extract emotions - look for different patterns
            emotions = {}
            emotions_match = re.search(r"'emotions':\s*\{([^}]+)\}", output_str)
            if not emotions_match:
                emotions_match = re.search(r"emotions':\s*\{([^}]+)\}", output_str)
            if emotions_match:
                emotions_str = emotions_match.group(1)
                # Parse individual emotions like 'anger': 0.2, 'frustration': 0.4
                emotion_matches = re.findall(r"'([^']+)':\s*([\d.]+)", emotions_str)
                for emotion_name, emotion_value in emotion_matches:
                    emotions[emotion_name] = float(emotion_value)
            
            # Also look for emotions in text format
            if "Anger" in output_str and "Frustration" in output_str:
                anger_match = re.search(r"Anger\s*\(([\d.]+)\)", output_str)
                frustration_match = re.search(r"Frustration\s*\(([\d.]+)\)", output_str)
                if anger_match:
                    emotions['anger'] = float(anger_match.group(1))
                if frustration_match:
                    emotions['frustration'] = float(frustration_match.group(1))
            
            # Extract keywords - look for different patterns
            keywords = []
            keywords_match = re.search(r"'keywords':\s*\[([^\]]+)\]", output_str)
            if not keywords_match:
                keywords_match = re.search(r"keywords':\s*\[([^\]]+)\]", output_str)
            if keywords_match:
                keywords_str = keywords_match.group(1)
                # Parse keywords like 'product', 'broken', 'frustrated'
                keyword_matches = re.findall(r"'([^']+)'", keywords_str)
                keywords = keyword_matches
            
            # Also look for keywords in text format
            if "Keywords:" in output_str:
                keywords_text = re.search(r"Keywords:\s*([^,\n]+)", output_str)
                if keywords_text:
                    keywords.extend([kw.strip() for kw in keywords_text.group(1).split(',')])
            
            # Extract is_negative and is_positive - look for different patterns
            is_negative = ("'is_negative': True" in output_str or 
                          "is_negative': True" in output_str or
                          "negative sentiment" in output_str.lower() or
                          sentiment_score < -0.1)
            is_positive = ("'is_positive': True" in output_str or 
                          "is_positive': True" in output_str or
                          "positive sentiment" in output_str.lower() or
                          sentiment_score > 0.1)
            
            # Extract urgency_level
            urgency_match = re.search(r"'urgency_level':\s*'([^']+)'", output_str)
            urgency_level = urgency_match.group(1) if urgency_match else 'low'
            
            # Determine sentiment label from sentiment score
            if sentiment_score > 0.1:
                sentiment_label = "positive"
            elif sentiment_score < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            logger.info(f"Extracted sentiment data: score={sentiment_score}, confidence={confidence}, label={sentiment_label}")
            
            return {
                "overall_sentiment": sentiment_score,
                "sentiment_label": sentiment_label,
                "confidence_score": confidence,
                "positive_score": 1.0 if is_positive else 0.0,
                "negative_score": 1.0 if is_negative else 0.0,
                "neutral_score": 1.0 if not is_negative and not is_positive else 0.0,
                "anger_score": emotions.get("anger", 0.0),
                "confusion_score": emotions.get("confusion", 0.0),
                "delight_score": emotions.get("delight", 0.0),
                "frustration_score": emotions.get("frustration", 0.0),
                "analysis_method": "regex_parsing",
                "processing_time_ms": 1000,  # Default processing time
                "keywords": keywords,
                "entities": [],
                "topics": [],
                "emotions": emotions,
                "is_negative": is_negative,
                "is_positive": is_positive,
                "urgency_level": urgency_level,
                "raw_output": workflow_output
            }
        except Exception as e:
            logger.error(f"Error extracting sentiment analysis: {e}")
            # Return a safe default
            return {
                "overall_sentiment": 0.0,
                "sentiment_label": "neutral",
                "confidence_score": 0.5,
                "positive_score": 0.0,
                "negative_score": 0.0,
                "neutral_score": 1.0,
                "anger_score": 0.0,
                "confusion_score": 0.0,
                "delight_score": 0.0,
                "frustration_score": 0.0,
                "analysis_method": "regex_parsing_fallback",
                "processing_time_ms": 1000,
                "keywords": [],
                "entities": [],
                "topics": [],
                "emotions": {},
                "is_negative": False,
                "is_positive": False,
                "urgency_level": "low",
                "raw_output": workflow_output,
                "error": str(e)
            }
    
    def _extract_alerts(self, workflow_output: Any) -> list:
        """Extract alerts from workflow output"""
        try:
            output_str = str(workflow_output)
            
            # Look for alert-related information in the workflow output
            alerts = []
            
            # Check for high priority indicators
            if "high churn risk" in output_str.lower() or "escalation" in output_str.lower():
                alerts.append({
                    "type": "high_priority",
                    "message": "High churn risk detected - escalation recommended",
                    "severity": "high"
                })
            
            # Check for negative sentiment alerts
            if "negative sentiment" in output_str.lower() or "frustrated" in output_str.lower():
                alerts.append({
                    "type": "negative_sentiment",
                    "message": "Customer expressing negative sentiment",
                    "severity": "medium"
                })
            
            return alerts
        except Exception as e:
            logger.error(f"Error extracting alerts: {e}")
            return []
    
    def _extract_response_recommendations(self, workflow_output: Any) -> Optional[Dict[str, Any]]:
        """Extract response recommendations from workflow output"""
        try:
            output_str = str(workflow_output)
            
            # Look for response recommendations in the workflow output
            if "Dear [Customer Name]" in output_str or "response" in output_str.lower():
                # Extract the response content
                import re
                response_match = re.search(r"Dear \[Customer Name\](.*?)(?=Sincerely|Best regards|Thank you|$)", output_str, re.DOTALL)
                if response_match:
                    response_content = response_match.group(1).strip()
                    return {
                        "response_content": response_content,
                        "tone": "empathetic",
                        "urgency_handling": "immediate escalation recommended"
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error extracting response recommendations: {e}")
            return None
    
    def _extract_integration_status(self, workflow_output: Any) -> Dict[str, Any]:
        """Extract integration status from workflow output"""
        try:
            output_str = str(workflow_output)
            
            # Look for integration indicators in the workflow output
            slack_sent = "slack alert sent" in output_str.lower() or "slack notification sent" in output_str.lower()
            webhooks_triggered = "webhook delivered" in output_str.lower() or "crm updated" in output_str.lower()
            
            return {
                "slack_notifications_sent": slack_sent,
                "webhooks_triggered": webhooks_triggered,
                "integration_status": "completed" if (slack_sent or webhooks_triggered) else "unknown"
            }
        except Exception as e:
            logger.error(f"Error extracting integration status: {e}")
            return {
                "slack_notifications_sent": False,
                "webhooks_triggered": False,
                "integration_status": "unknown"
            }
    
    async def analyze_sentiment_only(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze sentiment only without full pipeline"""
        if not self._initialized:
            raise RuntimeError("Agent manager not initialized")
        
        # Create a minimal ticket for sentiment analysis
        from app.schemas.ticket import TicketCreate
        from datetime import datetime
        
        ticket_data = TicketCreate(
            ticket_id=f"sentiment-only-{datetime.now().timestamp()}",
            content=content,
            customer_email=context.get('customer_email', 'unknown') if context else 'unknown',
            channel=context.get('channel', 'chat') if context else 'chat',
            source=context.get('source', 'api') if context else 'api',
            priority=context.get('priority', 'normal') if context else 'normal'
        )
        
        # Use the simplified crew analyze_sentiment method directly
        from workflows.agent_crew import SentimentWatchdogCrew
        temp_crew = SentimentWatchdogCrew({})
        result = temp_crew.analyze_sentiment(content)
        return result
    
    async def check_trends(self, time_period: str = "1h") -> Dict[str, Any]:
        """Get current sentiment trends"""
        if not self._initialized:
            raise RuntimeError("Agent manager not initialized")
        
        # Get workflow status which includes trend information
        status = await self.workflow.get_workflow_status()
        
        # For now, return basic trend info
        # In a full implementation, this would query the database for trends
        return {
            "time_period": time_period,
            "total_tickets": 0,
            "positive_sentiment": 0,
            "negative_sentiment": 0,
            "neutral_sentiment": 0,
            "alerts_triggered": 0,
            "workflow_status": status
        }
    
    async def generate_response(self, ticket_data: TicketCreate, sentiment_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response recommendations for a ticket"""
        if not self._initialized:
            raise RuntimeError("Agent manager not initialized")
        
        # Process the ticket through the workflow to get response recommendations
        result = await self.process_ticket(ticket_data)
        return result.get('response_recommendations', {})
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow system"""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        return await self.workflow.get_workflow_status()
