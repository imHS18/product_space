"""
Risk Assessor Tool
Evaluates customer churn risk and escalation potential based on sentiment analysis
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class RiskAssessor(BaseTool):
    """Tool for assessing customer risk and escalation potential"""
    
    name: str = "Risk Assessor"
    description: str = "Evaluates customer churn risk and escalation potential based on sentiment analysis, customer data, and business context."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'risk_thresholds', {
            "critical": 0.9,
            "high": 0.7,
            "medium": 0.5,
            "low": 0.3
        })
        
        object.__setattr__(self, 'churn_indicators', [
            "cancel", "refund", "unsubscribe", "delete account", "close account",
            "never use again", "switch to competitor", "terrible service",
            "worst experience", "hate this", "useless", "waste of money"
        ])
        
        object.__setattr__(self, 'escalation_indicators', [
            "urgent", "asap", "immediately", "now", "critical", "emergency",
            "escalate", "manager", "supervisor", "ceo", "legal", "lawyer",
            "social media", "twitter", "facebook", "review", "complain"
        ])
    
    def _run(self, sentiment_result: str, ticket_data: str) -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        # In practice, you'd convert the strings back to dicts or handle JSON
        # For now, returning a simple risk assessment
        return "Risk assessment completed"
    
    def assess_risk(self, sentiment_result: Dict[str, Any], ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess customer risk and escalation potential
        
        Args:
            sentiment_result: Results from sentiment analysis
            ticket_data: Customer ticket information
            
        Returns:
            Dictionary with risk assessment results
        """
        try:
            # Extract key information
            text = sentiment_result.get("text", "").lower()
            overall_sentiment = sentiment_result.get("overall_sentiment", 0.0)
            emotions = sentiment_result.get("emotions", {})
            urgency_level = sentiment_result.get("urgency_level", "low")
            confidence = sentiment_result.get("confidence", 0.0)
            
            # Calculate risk factors
            churn_risk = self._calculate_churn_risk(text, overall_sentiment, emotions)
            escalation_risk = self._calculate_escalation_risk(text, urgency_level, emotions)
            business_impact = self._calculate_business_impact(ticket_data, churn_risk)
            response_urgency = self._calculate_response_urgency(escalation_risk, urgency_level)
            
            # Overall risk score
            overall_risk = self._calculate_overall_risk(
                churn_risk, escalation_risk, business_impact, response_urgency
            )
            
            risk_level = self._get_risk_level(overall_risk)
            
            return {
                "overall_risk": overall_risk,
                "risk_level": risk_level,
                "risk_factors": {
                    "churn_risk": churn_risk,
                    "escalation_risk": escalation_risk,
                    "business_impact": business_impact,
                    "response_urgency": response_urgency
                },
                "risk_indicators": {
                    "churn_indicators_found": self._find_churn_indicators(text),
                    "escalation_indicators_found": self._find_escalation_indicators(text),
                    "emotional_intensity": self._assess_emotional_intensity(emotions),
                    "urgency_signals": self._assess_urgency_signals(text, urgency_level)
                },
                "recommendations": self._generate_risk_recommendations(
                    risk_level, churn_risk, escalation_risk
                ),
                "priority_score": self._calculate_priority_score(overall_risk, response_urgency)
            }
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            return {
                "overall_risk": 0.5,
                "risk_level": "unknown",
                "error": str(e)
            }
    
    def _calculate_churn_risk(self, text: str, sentiment: float, emotions: Dict[str, float]) -> float:
        """Calculate customer churn risk"""
        churn_risk = 0.0
        
        # Base risk from negative sentiment
        if sentiment < -0.5:
            churn_risk += 0.4
        elif sentiment < -0.2:
            churn_risk += 0.2
        
        # Risk from churn indicators in text
        churn_indicators_found = self._find_churn_indicators(text)
        churn_risk += len(churn_indicators_found) * 0.15
        
        # Risk from emotional state
        anger = emotions.get("anger", 0.0)
        frustration = emotions.get("frustration", 0.0)
        
        if anger > 0.7 or frustration > 0.8:
            churn_risk += 0.3
        elif anger > 0.5 or frustration > 0.6:
            churn_risk += 0.2
        
        return min(1.0, churn_risk)
    
    def _calculate_escalation_risk(self, text: str, urgency_level: str, emotions: Dict[str, float]) -> float:
        """Calculate escalation risk"""
        escalation_risk = 0.0
        
        # Base risk from urgency level
        urgency_weights = {"high": 0.4, "medium": 0.2, "low": 0.1}
        escalation_risk += urgency_weights.get(urgency_level, 0.1)
        
        # Risk from escalation indicators
        escalation_indicators_found = self._find_escalation_indicators(text)
        escalation_risk += len(escalation_indicators_found) * 0.1
        
        # Risk from emotional intensity
        emotional_intensity = self._assess_emotional_intensity(emotions)
        if emotional_intensity == "high":
            escalation_risk += 0.3
        elif emotional_intensity == "medium":
            escalation_risk += 0.2
        
        return min(1.0, escalation_risk)
    
    def _calculate_business_impact(self, ticket_data: Dict[str, Any], churn_risk: float) -> float:
        """Calculate potential business impact"""
        impact = 0.0
        
        # Customer tier impact
        customer_tier = ticket_data.get("customer_tier", "standard")
        tier_weights = {
            "enterprise": 1.0,
            "premium": 0.8,
            "standard": 0.5,
            "basic": 0.3
        }
        impact += tier_weights.get(customer_tier, 0.5) * churn_risk
        
        # Account value impact
        account_value = ticket_data.get("account_value", 0)
        if account_value > 10000:
            impact += 0.2
        elif account_value > 1000:
            impact += 0.1
        
        # Historical relationship
        customer_since = ticket_data.get("customer_since")
        if customer_since:
            try:
                customer_date = datetime.fromisoformat(customer_since.replace('Z', '+00:00'))
                years_as_customer = (datetime.now() - customer_date).days / 365
                if years_as_customer > 2:
                    impact += 0.1  # Long-term customers are more valuable
            except:
                pass
        
        return min(1.0, impact)
    
    def _calculate_response_urgency(self, escalation_risk: float, urgency_level: str) -> float:
        """Calculate required response urgency"""
        urgency = 0.0
        
        # Base urgency from escalation risk
        urgency += escalation_risk * 0.6
        
        # Additional urgency from urgency level
        level_weights = {"high": 0.4, "medium": 0.2, "low": 0.1}
        urgency += level_weights.get(urgency_level, 0.1)
        
        return min(1.0, urgency)
    
    def _calculate_overall_risk(self, churn_risk: float, escalation_risk: float, 
                              business_impact: float, response_urgency: float) -> float:
        """Calculate overall risk score"""
        # Weighted combination of risk factors
        overall_risk = (
            churn_risk * 0.3 +
            escalation_risk * 0.25 +
            business_impact * 0.25 +
            response_urgency * 0.2
        )
        
        return min(1.0, overall_risk)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level based on score"""
        if risk_score >= self.risk_thresholds["critical"]:
            return "critical"
        elif risk_score >= self.risk_thresholds["high"]:
            return "high"
        elif risk_score >= self.risk_thresholds["medium"]:
            return "medium"
        elif risk_score >= self.risk_thresholds["low"]:
            return "low"
        else:
            return "minimal"
    
    def _find_churn_indicators(self, text: str) -> List[str]:
        """Find churn indicators in text"""
        found_indicators = []
        for indicator in self.churn_indicators:
            if indicator in text:
                found_indicators.append(indicator)
        return found_indicators
    
    def _find_escalation_indicators(self, text: str) -> List[str]:
        """Find escalation indicators in text"""
        found_indicators = []
        for indicator in self.escalation_indicators:
            if indicator in text:
                found_indicators.append(indicator)
        return found_indicators
    
    def _assess_emotional_intensity(self, emotions: Dict[str, float]) -> str:
        """Assess overall emotional intensity"""
        max_emotion = max(emotions.values()) if emotions else 0.0
        
        if max_emotion > 0.8:
            return "high"
        elif max_emotion > 0.5:
            return "medium"
        else:
            return "low"
    
    def _assess_urgency_signals(self, text: str, urgency_level: str) -> Dict[str, Any]:
        """Assess urgency signals in the text"""
        urgency_words = ["urgent", "asap", "immediately", "now", "critical", "emergency"]
        found_urgency_words = [word for word in urgency_words if word in text]
        
        return {
            "urgency_words_found": found_urgency_words,
            "urgency_level": urgency_level,
            "has_urgency_signals": len(found_urgency_words) > 0 or urgency_level != "low"
        }
    
    def _generate_risk_recommendations(self, risk_level: str, churn_risk: float, 
                                     escalation_risk: float) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == "critical":
            recommendations.extend([
                "Immediate escalation required",
                "Assign to senior support representative",
                "Consider executive outreach",
                "Monitor closely for 24-48 hours"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "Escalate within 2 hours",
                "Assign to experienced support representative",
                "Consider proactive outreach",
                "Monitor customer behavior closely"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Respond within 4 hours",
                "Assign to appropriate support tier",
                "Monitor for escalation signals",
                "Consider follow-up within 24 hours"
            ])
        else:  # low or minimal
            recommendations.extend([
                "Standard response time acceptable",
                "Monitor for pattern changes",
                "Consider proactive engagement if patterns emerge"
            ])
        
        # Specific recommendations based on risk types
        if churn_risk > 0.7:
            recommendations.append("High churn risk - consider retention strategies")
        
        if escalation_risk > 0.7:
            recommendations.append("High escalation risk - prepare escalation resources")
        
        return recommendations
    
    def _calculate_priority_score(self, overall_risk: float, response_urgency: float) -> float:
        """Calculate priority score for ticket routing"""
        # Priority is combination of risk and urgency
        priority = (overall_risk * 0.6 + response_urgency * 0.4)
        return min(1.0, priority)
