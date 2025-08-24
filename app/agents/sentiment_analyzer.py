"""
Sentiment Analyzer Agent using TextBlob and VADER for efficient sentiment analysis
"""

import asyncio
import logging
import time
from typing import Dict, Any, List
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.core.config import settings

logger = logging.getLogger(__name__)


class SentimentAnalyzerAgent:
    """AI Agent for sentiment analysis using efficient NLP models"""
    
    def __init__(self):
        self.textblob_analyzer = None
        self.vader_analyzer = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize sentiment analysis models"""
        if self._initialized:
            return
        
        logger.info("🔍 Initializing Sentiment Analyzer Agent...")
        
        try:
            # Initialize VADER sentiment analyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            
            # Test the analyzers
            test_text = "This is a test message."
            _ = self.vader_analyzer.polarity_scores(test_text)
            
            self._initialized = True
            logger.info("✅ Sentiment Analyzer Agent initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize sentiment analyzer: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup agent resources"""
        self._initialized = False
        logger.info("🧹 Sentiment Analyzer Agent cleaned up")
    
    async def analyze(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze sentiment of text content using multiple methods
        
        Args:
            content: Text content to analyze
            context: Additional context (ticket info, etc.)
            
        Returns:
            Dict containing sentiment analysis results
        """
        if not self._initialized:
            raise RuntimeError("Sentiment analyzer not initialized")
        
        start_time = time.time()
        
        try:
            # Clean and preprocess text
            cleaned_content = self._preprocess_text(content)
            
            # Analyze with VADER (primary method)
            vader_scores = self.vader_analyzer.polarity_scores(cleaned_content)
            
            # Analyze with TextBlob (secondary method)
            textblob_analysis = TextBlob(cleaned_content)
            textblob_sentiment = textblob_analysis.sentiment
            
            # Extract emotion indicators
            emotion_scores = self._analyze_emotions(cleaned_content)
            
            # Extract keywords and topics
            keywords = self._extract_keywords(cleaned_content)
            
            # Determine overall sentiment
            overall_sentiment = vader_scores['compound']
            
            # Calculate confidence based on agreement between methods
            confidence = self._calculate_confidence(vader_scores, textblob_sentiment)
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            result = {
                "overall_sentiment": overall_sentiment,
                "positive_score": vader_scores['pos'],
                "negative_score": vader_scores['neg'],
                "neutral_score": vader_scores['neu'],
                
                # Emotion analysis
                "anger_score": emotion_scores.get('anger', 0.0),
                "confusion_score": emotion_scores.get('confusion', 0.0),
                "delight_score": emotion_scores.get('delight', 0.0),
                "frustration_score": emotion_scores.get('frustration', 0.0),
                
                # Analysis metadata
                "analysis_method": "vader_textblob",
                "confidence_score": confidence,
                "processing_time_ms": int(processing_time),
                
                # Detailed analysis
                "keywords": keywords,
                "entities": [],  # Could be enhanced with NER
                "topics": self._extract_topics(cleaned_content),
                
                # Sentiment classification
                "is_negative": overall_sentiment < -settings.SENTIMENT_THRESHOLD,
                "is_positive": overall_sentiment > settings.SENTIMENT_THRESHOLD,
                "is_neutral": abs(overall_sentiment) <= settings.SENTIMENT_THRESHOLD,
                
                # Context
                "analyzed_content_length": len(content),
                "context": context or {}
            }
            
            logger.debug(f"Sentiment analysis completed in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Basic preprocessing
        text = text.strip()
        text = text.lower()
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotional indicators in text"""
        emotions = {
            'anger': 0.0,
            'confusion': 0.0,
            'delight': 0.0,
            'frustration': 0.0
        }
        
        # Anger indicators
        anger_words = ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated']
        emotions['anger'] = self._calculate_emotion_score(text, anger_words)
        
        # Confusion indicators
        confusion_words = ['confused', 'unclear', 'unsure', 'don\'t understand', 'what do you mean']
        emotions['confusion'] = self._calculate_emotion_score(text, confusion_words)
        
        # Delight indicators
        delight_words = ['happy', 'excited', 'great', 'amazing', 'wonderful', 'love it']
        emotions['delight'] = self._calculate_emotion_score(text, delight_words)
        
        # Frustration indicators
        frustration_words = ['frustrated', 'fed up', 'tired of', 'sick of', 'had enough']
        emotions['frustration'] = self._calculate_emotion_score(text, frustration_words)
        
        return emotions
    
    def _calculate_emotion_score(self, text: str, emotion_words: List[str]) -> float:
        """Calculate emotion score based on word presence and intensity"""
        text_lower = text.lower()
        score = 0.0
        
        for word in emotion_words:
            if word in text_lower:
                # Count occurrences and add intensity
                count = text_lower.count(word)
                score += count * 0.3  # Base intensity per occurrence
        
        # Normalize score to 0-1 range
        return min(score, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction based on frequency and importance
        words = text.split()
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        return [word for word, freq in keywords]
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simple topic extraction based on common support topics
        topics = []
        
        topic_keywords = {
            'billing': ['payment', 'bill', 'charge', 'invoice', 'subscription'],
            'technical': ['error', 'bug', 'crash', 'broken', 'not working'],
            'account': ['login', 'password', 'account', 'sign up', 'register'],
            'product': ['feature', 'product', 'service', 'functionality'],
            'refund': ['refund', 'money back', 'cancel', 'return']
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _calculate_confidence(self, vader_scores: Dict[str, float], textblob_sentiment: Any) -> float:
        """Calculate confidence score based on agreement between methods"""
        # Compare VADER compound score with TextBlob polarity
        vader_compound = vader_scores['compound']
        textblob_polarity = textblob_sentiment.polarity
        
        # Calculate agreement
        agreement = 1.0 - abs(vader_compound - textblob_polarity) / 2.0
        
        # Base confidence on agreement and VADER neutral score
        confidence = (agreement + vader_scores['neu']) / 2.0
        
        return min(confidence, 1.0)
