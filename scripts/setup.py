#!/usr/bin/env python3
"""
Setup script for Customer Sentiment Watchdog
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template"""
    env_content = """# Application Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///./sentiment_watchdog.db

# AI/LLM Configuration (Optional)
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Slack Integration (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
SLACK_CHANNEL=#support-alerts

# Sentiment Analysis Configuration
SENTIMENT_THRESHOLD=0.3
ALERT_COOLDOWN_MINUTES=15

# Performance Configuration
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT_SECONDS=5

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/sentiment_watchdog.log

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Cache Configuration (Optional)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=300
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists, skipping creation")
        return
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file")


def create_directories():
    """Create necessary directories"""
    directories = ["logs", "frontend"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import textblob
        import vaderSentiment
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: uv pip install -r requirements.txt")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up Customer Sentiment Watchdog")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run: python -m app.main")
    print("3. Open: http://localhost:8000")
    print("4. Test with: python scripts/test_api.py")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
