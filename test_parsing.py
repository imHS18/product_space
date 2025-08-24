#!/usr/bin/env python3
"""
Test script to verify sentiment parsing logic
"""

import re

def test_sentiment_parsing():
    # This is the actual tool output from the logs
    tool_output = """{'text': "I am extremely frustrated with the slow response times and the lack of updates on my order. This is unacceptable! I need this resolved immediately. I've been waiting for weeks and getting nowhere. The customer service is terrible and I'm very angry.", 'cleaned_text': "i am extremely frustrated with the slow response times and the lack of updates on my order. this is unacceptable! i need this resolved immediately. i've been waiting for weeks and getting nowhere. the customer service is terrible and i'm very angry.", 'vader_scores': {'neg': 0.297, 'neu': 0.668, 'pos': 0.035, 'compound': -0.9337}, 'textblob_sentiment': -0.68125, 'textblob_subjectivity': 0.65, 'emotions': {'anger': 0.2, 'frustration': 0.2, 'confusion': 0.0, 'satisfaction': 0.0, 'delight': 0.0, 'urgency': 0.6}, 'keywords': ['extremely', 'frustrated', 'slow', 'response', 'times', 'lack', 'updates', 'order.', 'this', 'unacceptable!'], 'overall_sentiment': -0.7645949999999999, 'confidence': 0.7894975, 'is_negative': True, 'is_positive': False, 'urgency_level': 'low', 'analysis_methods': ['vader', 'textblob', 'emotion_analysis']}"""
    
    print("Testing sentiment parsing with actual tool output:")
    print(f"Tool output: {tool_output}")
    print()
    
    # Test the parsing logic
    output_str = str(tool_output)
    
    # Extract overall_sentiment
    sentiment_match = re.search(r"'overall_sentiment':\s*([-\d.]+)", output_str)
    if not sentiment_match:
        sentiment_match = re.search(r"overall_sentiment':\s*([-\d.]+)", output_str)
    sentiment_score = float(sentiment_match.group(1)) if sentiment_match else 0.0
    
    # Extract confidence
    confidence_match = re.search(r"'confidence':\s*([\d.]+)", output_str)
    if not confidence_match:
        confidence_match = re.search(r"confidence':\s*([\d.]+)", output_str)
    confidence = float(confidence_match.group(1)) if confidence_match else 0.5
    
    # Extract emotions
    emotions = {}
    emotions_match = re.search(r"'emotions':\s*\{([^}]+)\}", output_str)
    if emotions_match:
        emotions_str = emotions_match.group(1)
        emotion_matches = re.findall(r"'([^']+)':\s*([\d.]+)", emotions_str)
        for emotion_name, emotion_value in emotion_matches:
            emotions[emotion_name] = float(emotion_value)
    
    # Extract keywords
    keywords = []
    keywords_match = re.search(r"'keywords':\s*\[([^\]]+)\]", output_str)
    if keywords_match:
        keywords_str = keywords_match.group(1)
        keyword_matches = re.findall(r"'([^']+)'", keywords_str)
        keywords = keyword_matches
    
    # Extract is_negative and is_positive
    is_negative = "'is_negative': True" in output_str
    is_positive = "'is_positive': True" in output_str
    
    # Extract urgency_level
    urgency_match = re.search(r"'urgency_level':\s*'([^']+)'", output_str)
    urgency_level = urgency_match.group(1) if urgency_match else 'low'
    
    # Determine sentiment label
    if sentiment_score > 0.1:
        sentiment_label = "positive"
    elif sentiment_score < -0.1:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"
    
    print("Parsing Results:")
    print(f"Sentiment Score: {sentiment_score}")
    print(f"Sentiment Label: {sentiment_label}")
    print(f"Confidence: {confidence}")
    print(f"Emotions: {emotions}")
    print(f"Keywords: {keywords}")
    print(f"Is Negative: {is_negative}")
    print(f"Is Positive: {is_positive}")
    print(f"Urgency Level: {urgency_level}")
    
    # Verify the results match expected values
    expected_score = -0.7645949999999999
    expected_confidence = 0.7894975
    
    print(f"\nVerification:")
    print(f"Expected sentiment score: {expected_score}")
    print(f"Actual sentiment score: {sentiment_score}")
    print(f"Match: {abs(sentiment_score - expected_score) < 0.001}")
    
    print(f"Expected confidence: {expected_confidence}")
    print(f"Actual confidence: {confidence}")
    print(f"Match: {abs(confidence - expected_confidence) < 0.001}")

if __name__ == "__main__":
    test_sentiment_parsing()
