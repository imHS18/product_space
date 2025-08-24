#!/usr/bin/env python3
"""
Direct test of sentiment analysis API
"""

import requests
import json

def test_sentiment_direct():
    """Test sentiment API directly"""
    url = "http://localhost:8000/api/v1/sentiment/analyze"
    
    test_data = {
        "text": "I am extremely frustrated with your service!"
    }
    
    print("Testing sentiment analysis API directly...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nParsed Response: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sentiment_direct()
