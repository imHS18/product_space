"""
Response Generator Agent for creating response recommendations
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ResponseGeneratorAgent:
    """AI Agent for generating response recommendations"""
    
    def __init__(self):
        self._initialized = False
    
    async def initialize(self):
        """Initialize response generator"""
        if self._initialized:
            return
        
        logger.info("💬 Initializing Response Generator Agent...")
        self._initialized = True
        logger.info("✅ Response Generator Agent initialized")
    
    async def cleanup(self):
        """Cleanup agent resources"""
        self._initialized = False
        logger.info("🧹 Response Generator Agent cleaned up")
    
    async def generate_recommendations(self, sentiment_result: Dict[str, Any], ticket_data: Any, alerts: List[Dict] = None) -> Dict[str, Any]:
        """Generate response recommendations based on sentiment analysis"""
        if not self._initialized:
            raise RuntimeError("Response generator not initialized")
        
        try:
            recommendations = {
                "response_tone": self._determine_response_tone(sentiment_result),
                "priority_actions": self._get_priority_actions(sentiment_result, ticket_data),
                "suggested_responses": self._generate_suggested_responses(sentiment_result, ticket_data),
                "escalation_needed": self._check_escalation_needed(sentiment_result, ticket_data),
                "follow_up_required": self._check_follow_up_needed(sentiment_result, ticket_data)
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    def _determine_response_tone(self, sentiment_result: Dict[str, Any]) -> str:
        """Determine appropriate response tone"""
        sentiment_score = sentiment_result["overall_sentiment"]
        anger_score = sentiment_result.get("anger_score", 0.0)
        frustration_score = sentiment_result.get("frustration_score", 0.0)
        
        if sentiment_score < -0.5 or anger_score > 0.5:
            return "empathetic_calm"
        elif sentiment_score < -0.2 or frustration_score > 0.3:
            return "understanding_supportive"
        elif sentiment_result.get("confusion_score", 0.0) > 0.3:
            return "clear_explanatory"
        else:
            return "professional_friendly"
    
    def _get_priority_actions(self, sentiment_result: Dict[str, Any], ticket_data: Any) -> List[str]:
        """Get priority actions for the support team"""
        actions = []
        
        # High urgency actions
        if sentiment_result["overall_sentiment"] < -0.5:
            actions.append("Immediate response within 1 hour")
        
        if sentiment_result.get("anger_score", 0.0) > 0.5:
            actions.append("Consider phone call or direct outreach")
        
        if ticket_data.priority in ["high", "urgent"]:
            actions.append("Escalate to senior support if needed")
        
        # Standard actions
        actions.append("Acknowledge customer's concern")
        actions.append("Provide clear timeline for resolution")
        
        return actions
    
    def _generate_suggested_responses(self, sentiment_result: Dict[str, Any], ticket_data: Any) -> List[str]:
        """Generate suggested response templates"""
        responses = []
        
        sentiment_score = sentiment_result["overall_sentiment"]
        anger_score = sentiment_result.get("anger_score", 0.0)
        confusion_score = sentiment_result.get("confusion_score", 0.0)
        
        # Base acknowledgment
        if sentiment_score < -0.3:
            responses.append("I understand your frustration and I'm here to help resolve this issue for you.")
        
        if confusion_score > 0.3:
            responses.append("Let me clarify this step by step to ensure we address your concern properly.")
        
        if anger_score > 0.3:
            responses.append("I want to assure you that we take this matter seriously and will work to resolve it promptly.")
        
        # Add specific response based on topics
        topics = sentiment_result.get("topics", [])
        if "billing" in topics:
            responses.append("I'll review your billing situation and provide a detailed explanation.")
        elif "technical" in topics:
            responses.append("I'll investigate this technical issue and provide you with a solution.")
        
        return responses
    
    def _check_escalation_needed(self, sentiment_result: Dict[str, Any], ticket_data: Any) -> bool:
        """Check if escalation is needed"""
        return (
            sentiment_result["overall_sentiment"] < -0.6 or
            sentiment_result.get("anger_score", 0.0) > 0.6 or
            ticket_data.priority == "urgent"
        )
    
    def _check_follow_up_needed(self, sentiment_result: Dict[str, Any], ticket_data: Any) -> bool:
        """Check if follow-up is needed"""
        return (
            sentiment_result["overall_sentiment"] < -0.3 or
            sentiment_result.get("frustration_score", 0.0) > 0.4
        )
