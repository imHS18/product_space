#!/usr/bin/env python3
"""
Debug script to see what the sentiment analyzer actually returns
"""

import sys
sys.path.append('.')

from tools.sentiment_analyzer import SentimentAnalyzer

def test_sentiment_analyzer():
    """Test the sentiment analyzer directly"""
    analyzer = SentimentAnalyzer()
    
    test_text = "I am extremely frustrated with your service!"
    
    print("Testing sentiment analyzer directly...")
    result = analyzer.analyze_sentiment(test_text)
    
    print("Result keys:", list(result.keys()))
    print("Full result:", result)

if __name__ == "__main__":
    test_sentiment_analyzer()
