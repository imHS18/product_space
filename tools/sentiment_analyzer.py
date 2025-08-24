"""
Sentiment Analyzer Tool
Provides sentiment analysis using multiple methods including VADER, TextBlob, and Google Gemini
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import google.generativeai as genai
from crewai.tools import BaseTool
from app.core.config import settings

logger = logging.getLogger(__name__)


class SentimentAnalyzer(BaseTool):
    """Tool for comprehensive sentiment analysis using multiple methods"""
    
    name: str = "Sentiment Analyzer"
    description: str = "Analyzes text sentiment using VADER, TextBlob, and optionally Google Gemini API. Returns comprehensive sentiment analysis with emotions, keywords, and confidence scores."
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation for these internal attributes
        object.__setattr__(self, 'vader_analyzer', SentimentIntensityAnalyzer())
        object.__setattr__(self, 'gemini_model', None)
        self._setup_gemini()
    
    def _setup_gemini(self):
        """Setup Google Gemini API if key is available"""
        if settings.GOOGLE_GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
                object.__setattr__(self, 'gemini_model', genai.GenerativeModel('gemini-pro'))
                logger.info("Google Gemini API configured successfully")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini API: {e}")
                object.__setattr__(self, 'gemini_model', None)
        else:
            logger.info("Google Gemini API key not provided, using VADER and TextBlob only")
    
    def _run(self, text: str) -> str:
        """Required method for CrewAI BaseTool - entry point for the tool"""
        result = self.analyze_sentiment(text)
        return str(result)
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using multiple methods
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # VADER analysis
            vader_scores = self.vader_analyzer.polarity_scores(cleaned_text)
            
            # TextBlob analysis
            blob = TextBlob(cleaned_text)
            textblob_sentiment = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # Emotion analysis
            emotions = self._analyze_emotions(cleaned_text)
            
            # Keywords extraction
            keywords = self._extract_keywords(cleaned_text)
            
            # Overall sentiment calculation
            overall_sentiment = self._calculate_overall_sentiment(
                vader_scores, textblob_sentiment, emotions
            )
            
            # Confidence scoring
            confidence = self._calculate_confidence(vader_scores, textblob_sentiment)
            
            return {
                "text": text,
                "cleaned_text": cleaned_text,
                "vader_scores": vader_scores,
                "textblob_sentiment": textblob_sentiment,
                "textblob_subjectivity": textblob_subjectivity,
                "emotions": emotions,
                "keywords": keywords,
                "overall_sentiment": overall_sentiment,
                "confidence": confidence,
                "is_negative": overall_sentiment < -settings.SENTIMENT_THRESHOLD,
                "is_positive": overall_sentiment > settings.SENTIMENT_THRESHOLD,
                "urgency_level": self._assess_urgency(emotions, vader_scores),
                "analysis_methods": ["vader", "textblob", "emotion_analysis"]
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                "text": text,
                "error": str(e),
                "overall_sentiment": 0.0,
                "confidence": 0.0,
                "is_negative": False,
                "is_positive": False
            }
    
    async def analyze_with_gemini(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze sentiment using Google Gemini API
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with Gemini analysis results or None if not available
        """
        if not self.gemini_model:
            return None
            
        try:
            prompt = f"""
            Analyze the sentiment of this customer support text. Provide a detailed analysis including:
            1. Overall sentiment (positive/negative/neutral)
            2. Emotional tone (frustrated, angry, confused, satisfied, etc.)
            3. Urgency level (low/medium/high)
            4. Key concerns or pain points
            5. Suggested response tone
            
            Text: "{text}"
            
            Respond in JSON format with these fields:
            - sentiment: string
            - emotional_tone: string
            - urgency_level: string
            - key_concerns: list of strings
            - suggested_tone: string
            - confidence: float (0-1)
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            
            # Parse response (simplified - in production you'd want more robust parsing)
            return {
                "gemini_analysis": response.text,
                "method": "gemini"
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {e}")
            return None
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Convert to lowercase
        text = text.lower()
        return text
    
    def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotional content of text"""
        emotions = {
            "anger": 0.0,
            "frustration": 0.0,
            "confusion": 0.0,
            "satisfaction": 0.0,
            "delight": 0.0,
            "urgency": 0.0
        }
        
        # Simple keyword-based emotion detection
        anger_words = ["angry", "furious", "mad", "outraged", "irritated", "annoyed"]
        frustration_words = ["frustrated", "disappointed", "upset", "unhappy", "dissatisfied"]
        confusion_words = ["confused", "unclear", "unsure", "don't understand", "unclear"]
        satisfaction_words = ["happy", "satisfied", "pleased", "great", "excellent", "good"]
        delight_words = ["amazing", "fantastic", "wonderful", "love", "perfect", "awesome"]
        urgency_words = ["urgent", "asap", "immediately", "now", "critical", "emergency"]
        
        text_lower = text.lower()
        
        for word in anger_words:
            if word in text_lower:
                emotions["anger"] += 0.2
                
        for word in frustration_words:
            if word in text_lower:
                emotions["frustration"] += 0.2
                
        for word in confusion_words:
            if word in text_lower:
                emotions["confusion"] += 0.2
                
        for word in satisfaction_words:
            if word in text_lower:
                emotions["satisfaction"] += 0.2
                
        for word in delight_words:
            if word in text_lower:
                emotions["delight"] += 0.2
                
        for word in urgency_words:
            if word in text_lower:
                emotions["urgency"] += 0.3
        
        # Normalize scores
        for emotion in emotions:
            emotions[emotion] = min(1.0, emotions[emotion])
        
        return emotions
    
    def _extract_keywords(self, text: str) -> list:
        """Extract important keywords from text"""
        # Simple keyword extraction (in production, you might use more sophisticated methods)
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = text.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Return top 10 keywords
        return keywords[:10]
    
    def _calculate_overall_sentiment(self, vader_scores: Dict, textblob_sentiment: float, emotions: Dict) -> float:
        """Calculate overall sentiment score"""
        # Weight VADER more heavily as it's more reliable for social media/customer service text
        vader_weight = 0.6
        textblob_weight = 0.3
        emotion_weight = 0.1
        
        vader_score = vader_scores['compound']
        textblob_score = textblob_sentiment
        
        # Emotion adjustment
        emotion_score = 0.0
        if emotions["anger"] > 0.5 or emotions["frustration"] > 0.5:
            emotion_score = -0.3
        elif emotions["satisfaction"] > 0.5 or emotions["delight"] > 0.5:
            emotion_score = 0.3
        
        overall = (vader_score * vader_weight + 
                  textblob_score * textblob_weight + 
                  emotion_score * emotion_weight)
        
        return max(-1.0, min(1.0, overall))
    
    def _calculate_confidence(self, vader_scores: Dict, textblob_sentiment: float) -> float:
        """Calculate confidence in the sentiment analysis"""
        # Higher confidence when VADER and TextBlob agree
        vader_abs = abs(vader_scores['compound'])
        textblob_abs = abs(textblob_sentiment)
        
        agreement = 1.0 - abs(vader_abs - textblob_abs)
        base_confidence = (vader_abs + textblob_abs) / 2
        
        confidence = (base_confidence * 0.7 + agreement * 0.3)
        return min(1.0, confidence)
    
    def _assess_urgency(self, emotions: Dict, vader_scores: Dict) -> str:
        """Assess urgency level based on emotions and sentiment"""
        if emotions["urgency"] > 0.7 or emotions["anger"] > 0.8:
            return "high"
        elif emotions["frustration"] > 0.6 or emotions["confusion"] > 0.7:
            return "medium"
        else:
            return "low"
