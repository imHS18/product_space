"""
Response Creator Tool
Generates personalized customer response recommendations based on sentiment analysis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai
from crewai.tools import BaseTool
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResponseCreator(BaseTool):
    """Tool for generating personalized customer response recommendations"""
    
    name: str = "Response Creator"
    description: str = "Generates personalized customer response recommendations based on sentiment analysis, customer context, and best practices."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'gemini_model', None)
        object.__setattr__(self, 'response_templates', {})
        self._setup_gemini()
        self._load_templates()
    
    def _setup_gemini(self):
        """Setup Google Gemini API if key is available"""
        if settings.GOOGLE_GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
                object.__setattr__(self, 'gemini_model', genai.GenerativeModel('gemini-pro'))
                logger.info("Google Gemini API configured for response creation")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini API: {e}")
                object.__setattr__(self, 'gemini_model', None)
        else:
            logger.info("Google Gemini API key not provided, using template-based responses")
    
    def _run(self, sentiment_data: str, customer_data: str) -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        # In practice, you'd convert the strings back to dicts or handle JSON
        # For now, returning a simple response creation result
        return "Response recommendation created"
    
    def _load_templates(self):
        """Load response templates for different scenarios"""
        object.__setattr__(self, 'response_templates', {
            "negative_high": {
                "tone": "empathetic_and_urgent",
                "structure": [
                    "acknowledge_emotion",
                    "apologize_sincerely",
                    "take_immediate_action",
                    "provide_solution",
                    "follow_up_commitment"
                ],
                "key_phrases": [
                    "I understand how frustrating this must be",
                    "I sincerely apologize for this experience",
                    "I'm taking immediate action to resolve this",
                    "Here's what I'm doing right now",
                    "I'll personally follow up to ensure this is resolved"
                ]
            },
            "negative_medium": {
                "tone": "empathetic_and_helpful",
                "structure": [
                    "acknowledge_concern",
                    "show_understanding",
                    "provide_solution",
                    "offer_additional_help"
                ],
                "key_phrases": [
                    "I understand your concern",
                    "Let me help you with this",
                    "Here's what we can do",
                    "Is there anything else I can assist you with?"
                ]
            },
            "neutral": {
                "tone": "professional_and_helpful",
                "structure": [
                    "acknowledge_request",
                    "provide_information",
                    "offer_assistance"
                ],
                "key_phrases": [
                    "Thank you for reaching out",
                    "Here's the information you requested",
                    "Please let me know if you need anything else"
                ]
            },
            "positive": {
                "tone": "enthusiastic_and_appreciative",
                "structure": [
                    "express_gratitude",
                    "acknowledge_feedback",
                    "reinforce_positive_experience"
                ],
                "key_phrases": [
                    "Thank you so much for your feedback!",
                    "We're thrilled to hear about your positive experience",
                    "Your satisfaction is our top priority"
                ]
            }
        })
    
    async def create_response(self, sentiment_data: Dict[str, Any], 
                            customer_data: Dict[str, Any],
                            ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create personalized response recommendation
        
        Args:
            sentiment_data: Results from sentiment analysis
            customer_data: Customer information and context
            ticket_data: Original ticket information
            
        Returns:
            Dictionary with response recommendation
        """
        try:
            # Determine response category based on sentiment
            response_category = self._determine_response_category(sentiment_data)
            
            # Get appropriate template
            template = self.response_templates.get(response_category, self.response_templates["neutral"])
            
            # Generate personalized response
            if self.gemini_model:
                response_text = await self._generate_ai_response(
                    sentiment_data, customer_data, ticket_data, template
                )
            else:
                response_text = self._generate_template_response(
                    sentiment_data, customer_data, ticket_data, template
                )
            
            # Create response recommendation
            recommendation = {
                "response_text": response_text,
                "response_category": response_category,
                "tone": template["tone"],
                "urgency_level": self._determine_urgency_level(sentiment_data),
                "personalization_factors": self._identify_personalization_factors(customer_data),
                "suggested_actions": self._suggest_actions(sentiment_data, customer_data),
                "follow_up_required": self._determine_follow_up_need(sentiment_data),
                "confidence_score": self._calculate_confidence_score(sentiment_data, customer_data)
            }
            
            logger.info(f"Response recommendation created for {response_category} sentiment")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error creating response: {e}")
            return {
                "response_text": "Thank you for contacting us. We're looking into your request and will get back to you soon.",
                "response_category": "neutral",
                "error": str(e)
            }
    
    def _determine_response_category(self, sentiment_data: Dict[str, Any]) -> str:
        """Determine response category based on sentiment analysis"""
        sentiment_score = sentiment_data.get("sentiment_score", 0.0)
        emotions = sentiment_data.get("emotions", {})
        
        # Check for high negative emotions
        anger = emotions.get("anger", 0.0)
        frustration = emotions.get("frustration", 0.0)
        
        if sentiment_score < -0.5 or anger > 0.7 or frustration > 0.8:
            return "negative_high"
        elif sentiment_score < -0.1:
            return "negative_medium"
        elif sentiment_score > 0.3:
            return "positive"
        else:
            return "neutral"
    
    async def _generate_ai_response(self, sentiment_data: Dict[str, Any],
                                  customer_data: Dict[str, Any],
                                  ticket_data: Dict[str, Any],
                                  template: Dict[str, Any]) -> str:
        """Generate response using AI"""
        try:
            prompt = self._create_ai_prompt(sentiment_data, customer_data, ticket_data, template)
            
            response = await self.gemini_model.generate_content_async(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._generate_template_response(sentiment_data, customer_data, ticket_data, template)
    
    def _create_ai_prompt(self, sentiment_data: Dict[str, Any],
                         customer_data: Dict[str, Any],
                         ticket_data: Dict[str, Any],
                         template: Dict[str, Any]) -> str:
        """Create prompt for AI response generation"""
        
        customer_tier = customer_data.get("customer_tier", "standard")
        sentiment_score = sentiment_data.get("sentiment_score", 0.0)
        emotions = sentiment_data.get("emotions", {})
        content = ticket_data.get("content", "")
        
        prompt = f"""
You are a customer service expert creating a personalized response for a {customer_tier} customer.

Customer Context:
- Customer Tier: {customer_tier}
- Sentiment Score: {sentiment_score}
- Emotions Detected: {emotions}
- Original Message: "{content}"

Response Requirements:
- Tone: {template['tone']}
- Structure: {', '.join(template['structure'])}
- Key Phrases to Include: {', '.join(template['key_phrases'])}

Create a personalized, empathetic response that:
1. Acknowledges the customer's emotions and concerns
2. Provides a clear solution or next steps
3. Shows understanding of their situation
4. Maintains a professional yet warm tone
5. Is appropriate for their customer tier

Response (max 200 words):
"""
        return prompt
    
    def _generate_template_response(self, sentiment_data: Dict[str, Any],
                                  customer_data: Dict[str, Any],
                                  ticket_data: Dict[str, Any],
                                  template: Dict[str, Any]) -> str:
        """Generate response using template system"""
        
        # Get template structure and key phrases
        structure = template["structure"]
        key_phrases = template["key_phrases"]
        
        # Build response based on structure
        response_parts = []
        
        for step in structure:
            if step == "acknowledge_emotion":
                response_parts.append(key_phrases[0])
            elif step == "apologize_sincerely":
                response_parts.append(key_phrases[1])
            elif step == "take_immediate_action":
                response_parts.append(key_phrases[2])
            elif step == "provide_solution":
                response_parts.append(key_phrases[3])
            elif step == "follow_up_commitment":
                response_parts.append(key_phrases[4])
            elif step == "acknowledge_concern":
                response_parts.append(key_phrases[0])
            elif step == "show_understanding":
                response_parts.append("I can see why this is important to you.")
            elif step == "offer_additional_help":
                response_parts.append(key_phrases[3])
            elif step == "acknowledge_request":
                response_parts.append(key_phrases[0])
            elif step == "provide_information":
                response_parts.append("Here's what I found for you:")
            elif step == "express_gratitude":
                response_parts.append(key_phrases[0])
            elif step == "acknowledge_feedback":
                response_parts.append(key_phrases[1])
            elif step == "reinforce_positive_experience":
                response_parts.append(key_phrases[2])
        
        return " ".join(response_parts)
    
    def _determine_urgency_level(self, sentiment_data: Dict[str, Any]) -> str:
        """Determine urgency level for response"""
        sentiment_score = sentiment_data.get("sentiment_score", 0.0)
        emotions = sentiment_data.get("emotions", {})
        
        anger = emotions.get("anger", 0.0)
        frustration = emotions.get("frustration", 0.0)
        
        if sentiment_score < -0.7 or anger > 0.8 or frustration > 0.9:
            return "immediate"
        elif sentiment_score < -0.3 or anger > 0.5 or frustration > 0.6:
            return "high"
        elif sentiment_score < 0:
            return "medium"
        else:
            return "low"
    
    def _identify_personalization_factors(self, customer_data: Dict[str, Any]) -> List[str]:
        """Identify factors for personalization"""
        factors = []
        
        customer_tier = customer_data.get("customer_tier", "standard")
        if customer_tier == "enterprise":
            factors.append("enterprise_customer")
        elif customer_tier == "premium":
            factors.append("premium_customer")
        
        account_value = customer_data.get("account_value", 0)
        if account_value > 10000:
            factors.append("high_value_customer")
        
        customer_since = customer_data.get("customer_since")
        if customer_since:
            factors.append("existing_customer")
        
        return factors
    
    def _suggest_actions(self, sentiment_data: Dict[str, Any], 
                        customer_data: Dict[str, Any]) -> List[str]:
        """Suggest actions based on sentiment and customer context"""
        actions = []
        
        sentiment_score = sentiment_data.get("sentiment_score", 0.0)
        customer_tier = customer_data.get("customer_tier", "standard")
        
        if sentiment_score < -0.5:
            actions.append("immediate_escalation")
            actions.append("personal_follow_up")
            if customer_tier in ["enterprise", "premium"]:
                actions.append("executive_outreach")
        elif sentiment_score < -0.2:
            actions.append("priority_handling")
            actions.append("detailed_response")
        elif sentiment_score > 0.5:
            actions.append("positive_feedback_acknowledgment")
            actions.append("loyalty_program_notification")
        
        return actions
    
    def _determine_follow_up_need(self, sentiment_data: Dict[str, Any]) -> bool:
        """Determine if follow-up is required"""
        sentiment_score = sentiment_data.get("sentiment_score", 0.0)
        emotions = sentiment_data.get("emotions", {})
        
        anger = emotions.get("anger", 0.0)
        frustration = emotions.get("frustration", 0.0)
        
        return sentiment_score < -0.3 or anger > 0.6 or frustration > 0.7
    
    def _calculate_confidence_score(self, sentiment_data: Dict[str, Any], 
                                  customer_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the response recommendation"""
        confidence = 0.5  # Base confidence
        
        # Sentiment confidence
        sentiment_confidence = sentiment_data.get("confidence", 0.5)
        confidence += sentiment_confidence * 0.3
        
        # Customer data completeness
        customer_fields = ["customer_tier", "account_value", "customer_since"]
        completeness = sum(1 for field in customer_fields if customer_data.get(field)) / len(customer_fields)
        confidence += completeness * 0.2
        
        return min(1.0, confidence)
    
    def get_response_templates(self) -> Dict[str, Any]:
        """Get available response templates"""
        return {
            "templates": self.response_templates,
            "total_templates": len(self.response_templates),
            "ai_enabled": self.gemini_model is not None
        }
    
    def add_custom_template(self, category: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Add custom response template"""
        try:
            self.response_templates[category] = template
            logger.info(f"Added custom template for category: {category}")
            return {"success": True, "category": category}
        except Exception as e:
            logger.error(f"Error adding custom template: {e}")
            return {"success": False, "error": str(e)}
