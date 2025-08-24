#!/usr/bin/env python3
"""
Test script to verify sentiment parsing logic with actual final output
"""

import re

def test_final_output_parsing():
    # This is the actual final output from the workflow
    final_output = """Complete workflow summary with data persistence confirmation:

1.  **Data Persistence:**
    *   Ticket and analysis data saved to the database. This includes the customer's negative sentiment, the confidence score, emotional insights (anger, frustration), urgency level, keywords, and the overall sentiment score. The customer's statement and the detailed context of the issue (damaged product, poor packaging, delayed delivery) are also stored.
    *   Trend aggregations updated in the database to reflect the negative sentiment and high churn risk.

2.  **Task Routing:**
    *   The customer escalation task was routed to a senior agent with high priority.

3.  **Workflow Monitoring:**
    *   The Slack notification confirms the initiation of the escalation plan.
    *   The database operations confirm data persistence.
    *   The Task Router confirms the task routing."""

    print("Testing sentiment parsing with actual final output:")
    print(f"Final output: {final_output}")
    print()
    
    # Test the parsing logic
    output_str = str(final_output)
    
    # Extract sentiment score - look for the specific pattern from the final output
    sentiment_match = re.search(r"The overall sentiment score is ([-\d.]+)", output_str)
    if not sentiment_match:
        sentiment_match = re.search(r"sentiment score of ([-\d.]+)", output_str)
    if not sentiment_match:
        sentiment_match = re.search(r"sentiment score is ([-\d.]+)", output_str)
    if not sentiment_match:
        sentiment_match = re.search(r"overall sentiment score is ([-\d.]+)", output_str)
    if not sentiment_match:
        sentiment_match = re.search(r"overall sentiment score of ([-\d.]+)", output_str)
    if not sentiment_match:
        sentiment_match = re.search(r"negative sentiment with an overall sentiment score of ([-\d.]+)", output_str)
    if not sentiment_match:
        sentiment_match = re.search(r"negative sentiment.*?([-\d.]+)", output_str)
    if not sentiment_match:
        # Look for any number that could be a sentiment score
        sentiment_match = re.search(r"sentiment.*?([-\d.]+)", output_str)
    
    # Safely convert sentiment score to float
    try:
        sentiment_score = float(sentiment_match.group(1)) if sentiment_match else 0.0
    except (ValueError, AttributeError):
        sentiment_score = 0.0
    
    # Extract confidence - look for the specific pattern from the final output
    confidence_match = re.search(r"confidence score of ([-\d.]+)", output_str)
    if not confidence_match:
        confidence_match = re.search(r"confidence.*?at ([-\d.]+)", output_str)
    if not confidence_match:
        confidence_match = re.search(r"confidence.*?([-\d.]+)", output_str)
    if not confidence_match:
        confidence_match = re.search(r"confidence score is ([-\d.]+)", output_str)
    if not confidence_match:
        # Look for any number that could be a confidence score
        confidence_match = re.search(r"confidence.*?([-\d.]+)", output_str)
    
    # Safely convert confidence to float
    try:
        confidence = float(confidence_match.group(1)) if confidence_match else 0.5
    except (ValueError, AttributeError):
        confidence = 0.5
    
    # Extract emotions from text like "anger (0.2) and frustration (0.2)"
    emotions = {}
    emotion_matches = re.findall(r"(\w+)\s*\(([-\d.]+)\)", output_str)
    for emotion_name, emotion_value in emotion_matches:
        try:
            emotions[emotion_name.lower()] = float(emotion_value)
        except (ValueError, AttributeError):
            pass
    
    # Extract keywords from text like "extremely frustrated," "slow response times,"
    keywords = []
    if "Keywords highlighting" in output_str:
        keywords_section = output_str.split("Keywords highlighting")[1].split(".")[0]
        keyword_matches = re.findall(r'"([^"]+)"', keywords_section)
        keywords = keyword_matches
    
    # Determine sentiment label
    if sentiment_score > 0.1:
        sentiment_label = "positive"
    elif sentiment_score < -0.1:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"
    
    # Determine is_negative and is_positive
    is_negative = sentiment_score < -0.1 or "negative" in output_str.lower()
    is_positive = sentiment_score > 0.1 or "positive" in output_str.lower()
    
    print("Parsing Results:")
    print(f"Sentiment Score: {sentiment_score}")
    print(f"Sentiment Label: {sentiment_label}")
    print(f"Confidence: {confidence}")
    print(f"Emotions: {emotions}")
    print(f"Keywords: {keywords}")
    print(f"Is Negative: {is_negative}")
    print(f"Is Positive: {is_positive}")
    print(f"Urgency Level: {'high' if 'urgent' in output_str.lower() else 'low'}")
    
    # Check if we found the sentiment data
    if sentiment_score == 0.0:
        print("\n❌ FAILED: Could not extract sentiment score from final output")
        print("The final output doesn't contain the sentiment score in the expected format")
    else:
        print(f"\n✅ SUCCESS: Extracted sentiment score: {sentiment_score}")

if __name__ == "__main__":
    test_final_output_parsing()
