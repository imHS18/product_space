# 🚀 Setup Guide - Customer Sentiment Watchdog

## Quick Setup

### 1. Install Dependencies
```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 2. Create Environment File
Create a `.env` file in the root directory with the following content:

```env
# Application Configuration
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
```

### 3. Run the Application
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### 4. Test the System
```bash
# Test API endpoints
python scripts/test_api.py

# Test workflow directly
python scripts/demo_workflow.py
```

## Environment Variables Explained

### Required Configuration
- `DATABASE_URL`: SQLite database path (default: `sqlite:///./sentiment_watchdog.db`)
- `DEBUG`: Enable debug mode (default: `true`)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)

### Optional AI/LLM Configuration
- `GOOGLE_GEMINI_API_KEY`: Your Google Gemini API key for advanced AI features
- `ANTHROPIC_API_KEY`: Your Anthropic API key (alternative to Gemini)

### Optional Slack Integration
- `SLACK_WEBHOOK_URL`: Slack incoming webhook URL for notifications
- `SLACK_CHANNEL`: Channel to send alerts to (default: `#support-alerts`)

### Sentiment Analysis Configuration
- `SENTIMENT_THRESHOLD`: Minimum negative sentiment score to trigger alerts (default: `0.3`)
- `ALERT_COOLDOWN_MINUTES`: Time between alerts for the same channel (default: `15`)

### Performance Configuration
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent ticket processing (default: `10`)
- `REQUEST_TIMEOUT_SECONDS`: Maximum processing time per request (default: `5`)

### Logging Configuration
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `LOG_FILE`: Log file path (default: `logs/sentiment_watchdog.log`)

## Getting API Keys

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### Slack Webhook URL
1. Go to your Slack workspace settings
2. Create a new app or use an existing one
3. Enable Incoming Webhooks
4. Create a webhook for your desired channel
5. Copy the webhook URL to your `.env` file

## Directory Structure
```
customer-sentiment-watchdog/
├── app/                    # FastAPI application
├── agent/                  # CrewAI agent definitions
├── tools/                  # Custom tools for agents
├── workflows/              # Workflow orchestration
├── frontend/               # Dashboard files
├── scripts/                # Test and utility scripts
├── logs/                   # Application logs
├── .env                    # Environment configuration
└── requirements.txt        # Python dependencies
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Database Errors**: The SQLite database will be created automatically on first run

3. **Port Already in Use**: Change the `PORT` in your `.env` file

4. **Missing API Keys**: The system works without API keys, but advanced features will be limited

### Health Checks
- Basic health: `GET http://localhost:8000/health`
- Detailed health: `GET http://localhost:8000/health/detailed`
- Workflow status: `GET http://localhost:8000/health/workflow`

## Next Steps

1. **Start the API**: `python -m app.main`
2. **Test endpoints**: `python scripts/test_api.py`
3. **View dashboard**: Open `http://localhost:8000/frontend/index.html`
4. **Monitor logs**: Check `logs/sentiment_watchdog.log`

For more information, see the main [README.md](README.md) file.
