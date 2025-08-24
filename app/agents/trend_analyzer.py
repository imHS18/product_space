"""
Trend Analyzer Agent for tracking sentiment trends over time
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TrendAnalyzerAgent:
    """AI Agent for analyzing sentiment trends over time"""
    
    def __init__(self):
        self._initialized = False
        self._trend_cache = {}  # Simple in-memory cache for trends
    
    async def initialize(self):
        """Initialize trend analyzer"""
        if self._initialized:
            return
        
        logger.info("📈 Initializing Trend Analyzer Agent...")
        self._initialized = True
        logger.info("✅ Trend Analyzer Agent initialized")
    
    async def cleanup(self):
        """Cleanup agent resources"""
        self._initialized = False
        self._trend_cache.clear()
        logger.info("🧹 Trend Analyzer Agent cleaned up")
    
    async def update_trends(self, sentiment_result: Dict[str, Any], ticket_data: Any):
        """Update trend analysis with new sentiment data"""
        if not self._initialized:
            raise RuntimeError("Trend analyzer not initialized")
        
        try:
            # Store sentiment data for trend calculation
            trend_key = f"{ticket_data.channel}_{ticket_data.source}"
            
            if trend_key not in self._trend_cache:
                self._trend_cache[trend_key] = []
            
            trend_data = {
                "timestamp": datetime.now(),
                "sentiment_score": sentiment_result["overall_sentiment"],
                "positive_score": sentiment_result["positive_score"],
                "negative_score": sentiment_result["negative_score"],
                "neutral_score": sentiment_result["neutral_score"],
                "anger_score": sentiment_result.get("anger_score", 0.0),
                "frustration_score": sentiment_result.get("frustration_score", 0.0),
                "ticket_priority": ticket_data.priority
            }
            
            self._trend_cache[trend_key].append(trend_data)
            
            # Keep only recent data (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self._trend_cache[trend_key] = [
                data for data in self._trend_cache[trend_key]
                if data["timestamp"] > cutoff_time
            ]
            
            logger.debug(f"Updated trends for {trend_key}")
            
        except Exception as e:
            logger.error(f"Error updating trends: {e}")
            raise
    
    async def get_trends(self, time_period: str = "1h") -> Dict[str, Any]:
        """Get current sentiment trends"""
        if not self._initialized:
            raise RuntimeError("Trend analyzer not initialized")
        
        try:
            trends = {}
            
            for trend_key, trend_data in self._trend_cache.items():
                if not trend_data:
                    continue
                
                # Calculate time window
                if time_period == "1h":
                    cutoff_time = datetime.now() - timedelta(hours=1)
                elif time_period == "6h":
                    cutoff_time = datetime.now() - timedelta(hours=6)
                elif time_period == "24h":
                    cutoff_time = datetime.now() - timedelta(hours=24)
                else:
                    cutoff_time = datetime.now() - timedelta(hours=1)
                
                # Filter data for time period
                recent_data = [
                    data for data in trend_data
                    if data["timestamp"] > cutoff_time
                ]
                
                if not recent_data:
                    continue
                
                # Calculate trend metrics
                trend_metrics = self._calculate_trend_metrics(recent_data)
                trends[trend_key] = trend_metrics
            
            return {
                "trends": trends,
                "time_period": time_period,
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            raise
    
    def _calculate_trend_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trend metrics from sentiment data"""
        if not data:
            return {}
        
        # Calculate averages
        avg_sentiment = sum(d["sentiment_score"] for d in data) / len(data)
        avg_positive = sum(d["positive_score"] for d in data) / len(data)
        avg_negative = sum(d["negative_score"] for d in data) / len(data)
        avg_neutral = sum(d["neutral_score"] for d in data) / len(data)
        avg_anger = sum(d["anger_score"] for d in data) / len(data)
        avg_frustration = sum(d["frustration_score"] for d in data) / len(data)
        
        # Calculate trend direction
        if len(data) >= 2:
            recent_sentiment = data[-1]["sentiment_score"]
            older_sentiment = data[0]["sentiment_score"]
            sentiment_change = recent_sentiment - older_sentiment
            
            if sentiment_change > 0.1:
                trend_direction = "improving"
            elif sentiment_change < -0.1:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        else:
            sentiment_change = 0.0
            trend_direction = "stable"
        
        # Count sentiment categories
        negative_count = sum(1 for d in data if d["sentiment_score"] < -0.1)
        positive_count = sum(1 for d in data if d["sentiment_score"] > 0.1)
        neutral_count = sum(1 for d in data if -0.1 <= d["sentiment_score"] <= 0.1)
        
        # Calculate percentages
        total_count = len(data)
        negative_percentage = (negative_count / total_count) * 100 if total_count > 0 else 0
        positive_percentage = (positive_count / total_count) * 100 if total_count > 0 else 0
        neutral_percentage = (neutral_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            "total_tickets": total_count,
            "avg_sentiment": avg_sentiment,
            "avg_positive_score": avg_positive,
            "avg_negative_score": avg_negative,
            "avg_neutral_score": avg_neutral,
            "avg_anger_score": avg_anger,
            "avg_frustration_score": avg_frustration,
            "sentiment_change": sentiment_change,
            "trend_direction": trend_direction,
            "negative_count": negative_count,
            "positive_count": positive_count,
            "neutral_count": neutral_count,
            "negative_percentage": negative_percentage,
            "positive_percentage": positive_percentage,
            "neutral_percentage": neutral_percentage,
            "time_range": {
                "start": data[0]["timestamp"].isoformat(),
                "end": data[-1]["timestamp"].isoformat()
            }
        }
