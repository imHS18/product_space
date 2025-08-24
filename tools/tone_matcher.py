"""
Tone Matcher Tool
Matches and adjusts response tone to align with customer's emotional state
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class ToneMatcher(BaseTool):
    """Tool for matching and adjusting response tone to align with customer's emotional state"""
    
    name: str = "Tone Matcher"
    description: str = "Analyzes customer tone and adjusts response tone to create better emotional alignment and communication effectiveness."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'tone_profiles', {})
        object.__setattr__(self, 'tone_adjustment_rules', {})
        self._load_tone_profiles()
        self._load_adjustment_rules()
    
    def _run(self, customer_tone: str, response_tone: str) -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        # In practice, you'd convert the strings back to proper types or handle JSON
        # For now, returning a simple tone matching result
        return f"Tone matched: {customer_tone} -> {response_tone}"
    
    def _load_tone_profiles(self):
        """Load tone profiles for different emotional states"""
        object.__setattr__(self, 'tone_profiles', {
            "angry": {
                "characteristics": ["direct", "firm", "empathetic", "action-oriented"],
                "language_style": "clear_and_decisive",
                "emotional_approach": "de_escalating",
                "response_speed": "immediate",
                "formality_level": "professional_but_warm"
            },
            "frustrated": {
                "characteristics": ["understanding", "supportive", "solution-focused", "patient"],
                "language_style": "explanatory_and_helpful",
                "emotional_approach": "validating",
                "response_speed": "quick",
                "formality_level": "conversational"
            },
            "confused": {
                "characteristics": ["clear", "educational", "step_by_step", "reassuring"],
                "language_style": "simple_and_structured",
                "emotional_approach": "guiding",
                "response_speed": "thorough",
                "formality_level": "friendly"
            },
            "anxious": {
                "characteristics": ["calming", "reassuring", "detailed", "supportive"],
                "language_style": "gentle_and_informative",
                "emotional_approach": "soothing",
                "response_speed": "prompt",
                "formality_level": "warm_and_professional"
            },
            "neutral": {
                "characteristics": ["professional", "efficient", "helpful", "clear"],
                "language_style": "standard_business",
                "emotional_approach": "balanced",
                "response_speed": "normal",
                "formality_level": "professional"
            },
            "satisfied": {
                "characteristics": ["appreciative", "encouraging", "helpful", "positive"],
                "language_style": "enthusiastic_and_supportive",
                "emotional_approach": "reinforcing",
                "response_speed": "normal",
                "formality_level": "friendly"
            },
            "delighted": {
                "characteristics": ["enthusiastic", "grateful", "celebratory", "supportive"],
                "language_style": "excited_and_appreciative",
                "emotional_approach": "amplifying",
                "response_speed": "normal",
                "formality_level": "casual_and_friendly"
            }
        })
    
    def _load_adjustment_rules(self):
        """Load rules for tone adjustments"""
        object.__setattr__(self, 'tone_adjustment_rules', {
            "emotional_alignment": {
                "match_intensity": True,
                "mirror_positive_emotions": True,
                "counter_negative_emotions": True,
                "maintain_professionalism": True
            },
            "customer_tier_adjustments": {
                "enterprise": {
                    "formality_increase": 0.2,
                    "detail_level": "high",
                    "response_structure": "formal"
                },
                "premium": {
                    "formality_increase": 0.1,
                    "detail_level": "medium_high",
                    "response_structure": "semi_formal"
                },
                "standard": {
                    "formality_increase": 0.0,
                    "detail_level": "medium",
                    "response_structure": "conversational"
                }
            },
            "urgency_adjustments": {
                "immediate": {
                    "response_length": "concise",
                    "action_emphasis": "high",
                    "tone_directness": "high"
                },
                "high": {
                    "response_length": "moderate",
                    "action_emphasis": "medium",
                    "tone_directness": "medium"
                },
                "normal": {
                    "response_length": "standard",
                    "action_emphasis": "low",
                    "tone_directness": "low"
                }
            }
        })
    
    def analyze_customer_tone(self, sentiment_data: Dict[str, Any], 
                            customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze customer's tone from sentiment data and customer context
        
        Args:
            sentiment_data: Results from sentiment analysis
            customer_data: Customer information and context
            
        Returns:
            Dictionary with tone analysis results
        """
        try:
            emotions = sentiment_data.get("emotions", {})
            sentiment_score = sentiment_data.get("sentiment_score", 0.0)
            
            # Determine primary emotional state
            primary_emotion = self._identify_primary_emotion(emotions, sentiment_score)
            
            # Get tone profile
            tone_profile = self.tone_profiles.get(primary_emotion, self.tone_profiles["neutral"])
            
            # Analyze tone characteristics
            tone_analysis = {
                "primary_emotion": primary_emotion,
                "tone_profile": tone_profile,
                "emotional_intensity": self._calculate_emotional_intensity(emotions),
                "communication_style": self._analyze_communication_style(sentiment_data),
                "urgency_signals": self._detect_urgency_signals(sentiment_data),
                "formality_preference": self._determine_formality_preference(customer_data),
                "tone_confidence": self._calculate_tone_confidence(emotions, sentiment_score)
            }
            
            logger.info(f"Customer tone analyzed: {primary_emotion}")
            return tone_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing customer tone: {e}")
            return {
                "primary_emotion": "neutral",
                "tone_profile": self.tone_profiles["neutral"],
                "error": str(e)
            }
    
    def adjust_response_tone(self, response_text: str, customer_tone: Dict[str, Any],
                           customer_data: Dict[str, Any], urgency_level: str) -> Dict[str, Any]:
        """
        Adjust response tone to match customer's emotional state
        
        Args:
            response_text: Original response text
            customer_tone: Customer tone analysis
            customer_data: Customer information
            urgency_level: Urgency level for the response
            
        Returns:
            Dictionary with adjusted response and tone recommendations
        """
        try:
            primary_emotion = customer_tone.get("primary_emotion", "neutral")
            tone_profile = customer_tone.get("tone_profile", self.tone_profiles["neutral"])
            
            # Get adjustment rules
            adjustments = self._get_tone_adjustments(
                primary_emotion, customer_data, urgency_level
            )
            
            # Apply tone adjustments
            adjusted_response = self._apply_tone_adjustments(
                response_text, tone_profile, adjustments
            )
            
            # Create tone recommendations
            tone_recommendations = self._create_tone_recommendations(
                customer_tone, adjustments
            )
            
            return {
                "original_response": response_text,
                "adjusted_response": adjusted_response,
                "tone_adjustments": adjustments,
                "recommendations": tone_recommendations,
                "tone_alignment_score": self._calculate_tone_alignment(
                    customer_tone, adjustments
                )
            }
            
        except Exception as e:
            logger.error(f"Error adjusting response tone: {e}")
            return {
                "original_response": response_text,
                "adjusted_response": response_text,
                "error": str(e)
            }
    
    def _identify_primary_emotion(self, emotions: Dict[str, float], sentiment_score: float) -> str:
        """Identify the primary emotional state"""
        if not emotions:
            # Fall back to sentiment score
            if sentiment_score < -0.5:
                return "angry"
            elif sentiment_score < -0.2:
                return "frustrated"
            elif sentiment_score > 0.5:
                return "delighted"
            else:
                return "neutral"
        
        # Find the emotion with highest intensity
        max_emotion = max(emotions.items(), key=lambda x: x[1])
        emotion_name, intensity = max_emotion
        
        # Map emotion names to tone profiles
        emotion_mapping = {
            "anger": "angry",
            "frustration": "frustrated",
            "confusion": "confused",
            "anxiety": "anxious",
            "satisfaction": "satisfied",
            "joy": "delighted",
            "happiness": "delighted"
        }
        
        # Return mapped emotion or default to neutral
        return emotion_mapping.get(emotion_name, "neutral")
    
    def _calculate_emotional_intensity(self, emotions: Dict[str, float]) -> float:
        """Calculate overall emotional intensity"""
        if not emotions:
            return 0.0
        
        max_intensity = max(emotions.values())
        avg_intensity = sum(emotions.values()) / len(emotions)
        
        # Weight towards maximum intensity
        return (max_intensity * 0.7) + (avg_intensity * 0.3)
    
    def _analyze_communication_style(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer's communication style"""
        text = sentiment_data.get("text", "")
        keywords = sentiment_data.get("keywords", [])
        
        style_indicators = {
            "formality": self._assess_formality(text),
            "directness": self._assess_directness(text),
            "detail_level": self._assess_detail_level(text),
            "urgency": self._assess_urgency_indicators(text)
        }
        
        return style_indicators
    
    def _assess_formality(self, text: str) -> str:
        """Assess formality level of text"""
        formal_indicators = ["please", "thank you", "would you", "could you", "kindly"]
        informal_indicators = ["hey", "hi", "thanks", "gonna", "wanna", "!"]
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in text.lower())
        informal_count = sum(1 for indicator in informal_indicators if indicator in text.lower())
        
        if formal_count > informal_count:
            return "formal"
        elif informal_count > formal_count:
            return "informal"
        else:
            return "neutral"
    
    def _assess_directness(self, text: str) -> str:
        """Assess directness level of text"""
        direct_indicators = ["need", "want", "must", "urgent", "immediately", "now"]
        indirect_indicators = ["maybe", "perhaps", "if possible", "when convenient"]
        
        direct_count = sum(1 for indicator in direct_indicators if indicator in text.lower())
        indirect_count = sum(1 for indicator in indirect_indicators if indicator in text.lower())
        
        if direct_count > indirect_count:
            return "direct"
        elif indirect_count > direct_count:
            return "indirect"
        else:
            return "moderate"
    
    def _assess_detail_level(self, text: str) -> str:
        """Assess detail level of text"""
        word_count = len(text.split())
        
        if word_count > 100:
            return "detailed"
        elif word_count > 50:
            return "moderate"
        else:
            return "brief"
    
    def _assess_urgency_indicators(self, text: str) -> str:
        """Assess urgency indicators in text"""
        urgency_words = ["urgent", "asap", "immediately", "now", "critical", "emergency"]
        urgency_count = sum(1 for word in urgency_words if word in text.lower())
        
        if urgency_count >= 2:
            return "high"
        elif urgency_count == 1:
            return "medium"
        else:
            return "low"
    
    def _detect_urgency_signals(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect urgency signals in the communication"""
        text = sentiment_data.get("text", "")
        urgency_level = sentiment_data.get("urgency_level", "low")
        
        urgency_words = ["urgent", "asap", "immediately", "now", "critical", "emergency"]
        found_urgency_words = [word for word in urgency_words if word in text.lower()]
        
        return {
            "urgency_level": urgency_level,
            "urgency_words_found": found_urgency_words,
            "has_urgency_signals": len(found_urgency_words) > 0 or urgency_level != "low"
        }
    
    def _determine_formality_preference(self, customer_data: Dict[str, Any]) -> str:
        """Determine customer's formality preference"""
        customer_tier = customer_data.get("customer_tier", "standard")
        
        formality_preferences = {
            "enterprise": "formal",
            "premium": "semi_formal",
            "standard": "conversational",
            "basic": "casual"
        }
        
        return formality_preferences.get(customer_tier, "conversational")
    
    def _calculate_tone_confidence(self, emotions: Dict[str, float], sentiment_score: float) -> float:
        """Calculate confidence in tone analysis"""
        if not emotions:
            return 0.5  # Medium confidence for sentiment-only analysis
        
        # Higher confidence if emotions are clearly defined
        max_emotion = max(emotions.values()) if emotions else 0.0
        emotion_variance = sum((v - max_emotion) ** 2 for v in emotions.values()) / len(emotions) if emotions else 0.0
        
        # Higher confidence for clear dominant emotions
        clarity_score = max_emotion - (emotion_variance * 0.5)
        
        return min(1.0, max(0.0, clarity_score))
    
    def _get_tone_adjustments(self, primary_emotion: str, customer_data: Dict[str, Any],
                            urgency_level: str) -> Dict[str, Any]:
        """Get tone adjustments based on emotion, customer tier, and urgency"""
        adjustments = {}
        
        # Emotional alignment adjustments
        emotional_rules = self.tone_adjustment_rules["emotional_alignment"]
        adjustments.update(emotional_rules)
        
        # Customer tier adjustments
        customer_tier = customer_data.get("customer_tier", "standard")
        tier_adjustments = self.tone_adjustment_rules["customer_tier_adjustments"].get(
            customer_tier, self.tone_adjustment_rules["customer_tier_adjustments"]["standard"]
        )
        adjustments.update(tier_adjustments)
        
        # Urgency adjustments
        urgency_adjustments = self.tone_adjustment_rules["urgency_adjustments"].get(
            urgency_level, self.tone_adjustment_rules["urgency_adjustments"]["normal"]
        )
        adjustments.update(urgency_adjustments)
        
        return adjustments
    
    def _apply_tone_adjustments(self, response_text: str, tone_profile: Dict[str, Any],
                              adjustments: Dict[str, Any]) -> str:
        """Apply tone adjustments to response text"""
        # This is a simplified implementation
        # In a full implementation, you would use NLP to modify the text
        
        adjusted_text = response_text
        
        # Apply formality adjustments
        if adjustments.get("formality_increase", 0) > 0:
            # Make text more formal
            adjusted_text = self._increase_formality(adjusted_text)
        
        # Apply response length adjustments
        response_length = adjustments.get("response_length", "standard")
        if response_length == "concise":
            adjusted_text = self._make_concise(adjusted_text)
        
        # Apply action emphasis
        if adjustments.get("action_emphasis") == "high":
            adjusted_text = self._emphasize_actions(adjusted_text)
        
        return adjusted_text
    
    def _increase_formality(self, text: str) -> str:
        """Increase formality of text"""
        # Simple formality adjustments
        replacements = {
            "I'm": "I am",
            "you're": "you are",
            "we're": "we are",
            "don't": "do not",
            "can't": "cannot",
            "won't": "will not"
        }
        
        for informal, formal in replacements.items():
            text = text.replace(informal, formal)
        
        return text
    
    def _make_concise(self, text: str) -> str:
        """Make text more concise"""
        # Simple conciseness - remove unnecessary words
        # In practice, this would be more sophisticated
        sentences = text.split('.')
        concise_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence.split()) > 5:  # Keep meaningful sentences
                concise_sentences.append(sentence)
        
        return '. '.join(concise_sentences) + '.'
    
    def _emphasize_actions(self, text: str) -> str:
        """Emphasize action-oriented language"""
        # Add action emphasis words
        action_emphasis = [
            "I will immediately",
            "I am taking action to",
            "I'm working on this right now",
            "This is my priority"
        ]
        
        # Simple implementation - add emphasis to first sentence
        if text and not any(emphasis in text for emphasis in action_emphasis):
            first_sentence = text.split('.')[0] + '.'
            if "I" in first_sentence:
                text = text.replace(first_sentence, f"I will immediately {first_sentence.lower()}")
        
        return text
    
    def _create_tone_recommendations(self, customer_tone: Dict[str, Any],
                                   adjustments: Dict[str, Any]) -> List[str]:
        """Create tone recommendations for the response"""
        recommendations = []
        
        primary_emotion = customer_tone.get("primary_emotion", "neutral")
        
        # Emotion-specific recommendations
        if primary_emotion == "angry":
            recommendations.extend([
                "Use direct and firm language",
                "Acknowledge the frustration immediately",
                "Focus on immediate action steps",
                "Maintain professional composure"
            ])
        elif primary_emotion == "frustrated":
            recommendations.extend([
                "Show understanding and validation",
                "Provide clear explanations",
                "Offer step-by-step solutions",
                "Be patient and supportive"
            ])
        elif primary_emotion == "confused":
            recommendations.extend([
                "Use simple and clear language",
                "Break down complex information",
                "Provide examples when possible",
                "Ask clarifying questions if needed"
            ])
        
        # Add adjustment-based recommendations
        if adjustments.get("formality_increase", 0) > 0:
            recommendations.append("Increase formality level")
        
        if adjustments.get("action_emphasis") == "high":
            recommendations.append("Emphasize immediate actions")
        
        return recommendations
    
    def _calculate_tone_alignment(self, customer_tone: Dict[str, Any],
                                adjustments: Dict[str, Any]) -> float:
        """Calculate how well the response tone aligns with customer tone"""
        # Simplified alignment calculation
        alignment_score = 0.5  # Base score
        
        # Emotional alignment
        if adjustments.get("match_intensity", False):
            alignment_score += 0.2
        
        # Professionalism alignment
        if adjustments.get("maintain_professionalism", False):
            alignment_score += 0.2
        
        # Formality alignment
        formality_increase = adjustments.get("formality_increase", 0)
        if formality_increase > 0:
            alignment_score += 0.1
        
        return min(1.0, alignment_score)
    
    def get_tone_profiles(self) -> Dict[str, Any]:
        """Get available tone profiles"""
        return {
            "profiles": self.tone_profiles,
            "total_profiles": len(self.tone_profiles),
            "adjustment_rules": self.tone_adjustment_rules
        }
