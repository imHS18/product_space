"""
Confidence Scorer Tool
Evaluates the reliability and confidence of sentiment analysis results
"""

import logging
from typing import Dict, Any, List
from textblob import TextBlob
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class ConfidenceScorer(BaseTool):
    """Tool for evaluating confidence in sentiment analysis results"""
    
    name: str = "Confidence Scorer"
    description: str = "Evaluates the reliability and confidence of sentiment analysis results by analyzing agreement between methods, text quality, and signal strength."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'confidence_thresholds', {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        })
    
    def _run(self, sentiment_result: str) -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        # In practice, you'd convert the string back to dict or handle JSON
        # For now, returning a simple confidence assessment
        return "Confidence assessment completed"
    
    def evaluate_confidence(self, sentiment_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate confidence in sentiment analysis results
        
        Args:
            sentiment_result: Results from sentiment analysis
            
        Returns:
            Dictionary with confidence evaluation
        """
        try:
            # Extract key metrics
            vader_scores = sentiment_result.get("vader_scores", {})
            textblob_sentiment = sentiment_result.get("textblob_sentiment", 0.0)
            textblob_subjectivity = sentiment_result.get("textblob_subjectivity", 0.5)
            emotions = sentiment_result.get("emotions", {})
            keywords = sentiment_result.get("keywords", [])
            text_length = len(sentiment_result.get("text", ""))
            
            # Calculate confidence factors
            agreement_score = self._calculate_agreement_score(vader_scores, textblob_sentiment)
            subjectivity_score = self._calculate_subjectivity_score(textblob_subjectivity)
            emotion_consistency = self._calculate_emotion_consistency(emotions)
            text_quality = self._calculate_text_quality(text_length, keywords)
            signal_strength = self._calculate_signal_strength(vader_scores, emotions)
            
            # Overall confidence calculation
            overall_confidence = (
                agreement_score * 0.3 +
                subjectivity_score * 0.2 +
                emotion_consistency * 0.2 +
                text_quality * 0.15 +
                signal_strength * 0.15
            )
            
            confidence_level = self._get_confidence_level(overall_confidence)
            
            return {
                "overall_confidence": overall_confidence,
                "confidence_level": confidence_level,
                "confidence_factors": {
                    "agreement_score": agreement_score,
                    "subjectivity_score": subjectivity_score,
                    "emotion_consistency": emotion_consistency,
                    "text_quality": text_quality,
                    "signal_strength": signal_strength
                },
                "recommendations": self._generate_confidence_recommendations(
                    overall_confidence, confidence_level
                ),
                "reliability_warnings": self._check_reliability_warnings(
                    sentiment_result, overall_confidence
                )
            }
            
        except Exception as e:
            logger.error(f"Error in confidence evaluation: {e}")
            return {
                "overall_confidence": 0.0,
                "confidence_level": "unknown",
                "error": str(e)
            }
    
    def _calculate_agreement_score(self, vader_scores: Dict, textblob_sentiment: float) -> float:
        """Calculate agreement between different sentiment analysis methods"""
        if not vader_scores:
            return 0.5
        
        vader_compound = vader_scores.get('compound', 0.0)
        
        # Calculate agreement based on how close the scores are
        difference = abs(vader_compound - textblob_sentiment)
        agreement = max(0.0, 1.0 - difference)
        
        return agreement
    
    def _calculate_subjectivity_score(self, subjectivity: float) -> float:
        """Calculate confidence based on text subjectivity"""
        # Lower subjectivity often means more objective text, which can be more reliable
        # But very low subjectivity might indicate neutral text
        if subjectivity < 0.2:
            return 0.7  # Very objective, but might be neutral
        elif subjectivity < 0.5:
            return 0.9  # Good balance
        elif subjectivity < 0.8:
            return 0.6  # Somewhat subjective
        else:
            return 0.4  # Very subjective
    
    def _calculate_emotion_consistency(self, emotions: Dict[str, float]) -> float:
        """Calculate consistency of emotional signals"""
        if not emotions:
            return 0.5
        
        # Check if emotions are consistent (not conflicting)
        positive_emotions = emotions.get("satisfaction", 0.0) + emotions.get("delight", 0.0)
        negative_emotions = emotions.get("anger", 0.0) + emotions.get("frustration", 0.0)
        
        # If both positive and negative emotions are high, it's inconsistent
        if positive_emotions > 0.5 and negative_emotions > 0.5:
            return 0.3  # Conflicting emotions
        
        # If emotions are clear and strong, higher confidence
        max_emotion = max(emotions.values())
        if max_emotion > 0.7:
            return 0.9
        elif max_emotion > 0.4:
            return 0.7
        else:
            return 0.5
    
    def _calculate_text_quality(self, text_length: int, keywords: List[str]) -> float:
        """Calculate confidence based on text quality"""
        # Very short texts are less reliable
        if text_length < 10:
            return 0.3
        elif text_length < 50:
            return 0.6
        elif text_length < 200:
            return 0.8
        else:
            return 0.9
        
        # Could also consider keyword density, but keeping it simple for now
    
    def _calculate_signal_strength(self, vader_scores: Dict, emotions: Dict) -> float:
        """Calculate strength of sentiment signal"""
        if not vader_scores:
            return 0.5
        
        vader_compound = abs(vader_scores.get('compound', 0.0))
        
        # Stronger sentiment signals are more reliable
        if vader_compound > 0.7:
            return 0.9
        elif vader_compound > 0.4:
            return 0.7
        elif vader_compound > 0.2:
            return 0.5
        else:
            return 0.3
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level based on score"""
        if confidence >= self.confidence_thresholds["high"]:
            return "high"
        elif confidence >= self.confidence_thresholds["medium"]:
            return "medium"
        elif confidence >= self.confidence_thresholds["low"]:
            return "low"
        else:
            return "very_low"
    
    def _generate_confidence_recommendations(self, confidence: float, level: str) -> List[str]:
        """Generate recommendations based on confidence level"""
        recommendations = []
        
        if level == "very_low":
            recommendations.extend([
                "Consider manual review of this analysis",
                "Request additional context or clarification",
                "Use multiple analysis methods for verification"
            ])
        elif level == "low":
            recommendations.extend([
                "Proceed with caution",
                "Consider secondary analysis",
                "Monitor for pattern changes"
            ])
        elif level == "medium":
            recommendations.extend([
                "Analysis is reasonably reliable",
                "Consider context for final decision",
                "Monitor for consistency"
            ])
        else:  # high
            recommendations.extend([
                "Analysis is highly reliable",
                "Proceed with confidence",
                "Use as primary decision factor"
            ])
        
        return recommendations
    
    def _check_reliability_warnings(self, sentiment_result: Dict[str, Any], confidence: float) -> List[str]:
        """Check for potential reliability issues"""
        warnings = []
        
        # Check for very short text
        text = sentiment_result.get("text", "")
        if len(text) < 10:
            warnings.append("Very short text may not provide sufficient context")
        
        # Check for conflicting signals
        emotions = sentiment_result.get("emotions", {})
        positive_emotions = emotions.get("satisfaction", 0.0) + emotions.get("delight", 0.0)
        negative_emotions = emotions.get("anger", 0.0) + emotions.get("frustration", 0.0)
        
        if positive_emotions > 0.5 and negative_emotions > 0.5:
            warnings.append("Conflicting emotional signals detected")
        
        # Check for low confidence
        if confidence < 0.4:
            warnings.append("Low confidence score indicates potential unreliability")
        
        # Check for neutral sentiment
        overall_sentiment = sentiment_result.get("overall_sentiment", 0.0)
        if abs(overall_sentiment) < 0.1:
            warnings.append("Very neutral sentiment may indicate unclear intent")
        
        return warnings
