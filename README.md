# 🚨 Customer Sentiment Watchdog

A real-time sentiment analysis and alert system for customer support teams, built with FastAPI, SQLite, and AI agents.

## 🎯 Overview

The Customer Sentiment Watchdog is a high-performance system that:

- **Analyzes sentiment** of customer support tickets in real-time using efficient NLP models (TextBlob + VADER)
- **Detects negative sentiment** and automatically triggers alerts when thresholds are breached
- **Sends Slack notifications** for urgent customer issues requiring immediate attention
- **Tracks sentiment trends** over time to identify patterns and improvements
- **Provides response recommendations** to help support teams handle difficult situations
- **Maintains sub-5-second latency** for complete request-to-notification roundtrip

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI with async/await for high performance
- **Database**: SQLite with SQLAlchemy ORM for lightweight, zero-config storage
- **AI Agents**: Modular, collaborative agents for sentiment analysis, alerting, and response generation
- **Sentiment Analysis**: TextBlob + VADER for efficient, accurate sentiment detection
- **Notifications**: Slack integration with webhook support
- **Frontend**: Real-time dashboard with Chart.js visualizations

### AI Agent System
The system uses a **multi-agent workflow** powered by CrewAI that orchestrates specialized agents:

- **Sentiment Analysis Specialist**: Analyzes text sentiment using multiple methods (VADER, TextBlob, AI-powered)
- **Alert Decision Manager**: Assesses risk and determines when alerts should be triggered
- **Response Generation Specialist**: Creates personalized response recommendations for support teams
- **Integration Coordinator**: Manages Slack notifications and external webhook integrations
- **Workflow Orchestrator**: Coordinates the overall process and manages data persistence

### Workflow Process
1. **Sentiment Analysis**: Multi-method sentiment analysis with confidence scoring
2. **Risk Assessment**: Evaluate churn risk, escalation potential, and business impact
3. **Response Generation**: Create personalized responses with tone matching
4. **Integration**: Send notifications and trigger external systems
5. **Data Persistence**: Save results and update trend aggregations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- uv (recommended) or pip

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd customer-sentiment-watchdog
```

2. **Install dependencies with uv**
```bash
uv pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the application**
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### Environment Variables

Create a `.env` file with the following variables:

```env
# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./sentiment_watchdog.db

# AI/LLM (optional)
GOOGLE_GEMINI_API_KEY=your_google_gemini_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Slack Integration (optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url
SLACK_CHANNEL=#support-alerts

# Sentiment Analysis
SENTIMENT_THRESHOLD=0.3
ALERT_COOLDOWN_MINUTES=15

# Performance
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT_SECONDS=5
```

## 🔄 Workflow System

The Customer Sentiment Watchdog uses a sophisticated multi-agent workflow powered by CrewAI:

### Workflow Components
- **SentimentWatchdogWorkflow**: Main orchestrator that manages the entire process
- **5 Specialized Agents**: Each handling specific aspects of sentiment analysis and response
- **10 Custom Tools**: Providing specific functionality (sentiment analysis, risk assessment, etc.)
- **Sequential Processing**: Ensures each step builds on the previous one

### Workflow Steps
1. **Sentiment Analysis** → Multi-method analysis with confidence scoring
2. **Risk Assessment** → Evaluate churn risk and escalation potential  
3. **Response Generation** → Create personalized response recommendations
4. **Integration** → Send notifications and trigger external systems
5. **Data Persistence** → Save results and update trend aggregations

### Workflow Status
Check the workflow status and agent health:
```bash
GET /health/workflow
```

## 📊 API Endpoints

### Health Check
```bash
GET /health
GET /health/detailed
GET /health/workflow
```

### Tickets
```bash
POST /api/v1/tickets/                    # Create single ticket
POST /api/v1/tickets/bulk               # Create multiple tickets
GET /api/v1/tickets/                    # List tickets with pagination
GET /api/v1/tickets/{ticket_id}         # Get specific ticket
GET /api/v1/tickets/{ticket_id}/sentiment  # Get ticket sentiment
GET /api/v1/tickets/{ticket_id}/alerts  # Get ticket alerts
```

### Sentiment Analysis
```bash
POST /api/v1/sentiment/analyze          # Analyze text sentiment
```

### Trends
```bash
GET /api/v1/trends/?time_period=1h      # Get sentiment trends
```

### Alerts
```bash
GET /api/v1/alerts/                     # List alerts with pagination
GET /api/v1/alerts/{alert_id}           # Get specific alert
```

## 📝 Example Usage

### Create a Ticket

```bash
curl -X POST "http://localhost:8000/api/v1/tickets/" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TICKET-001",
    "channel": "email",
    "source": "zendesk",
    "customer_email": "angry.customer@example.com",
    "customer_name": "John Smith",
    "subject": "Very frustrated with service",
    "content": "I am extremely angry and frustrated with your terrible service! I've been waiting for 3 days and nobody has responded to my urgent request.",
    "priority": "urgent"
  }'
```

### Analyze Sentiment

```bash
curl -X POST "http://localhost:8000/api/v1/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I am very angry and frustrated with this terrible service!",
    "context": {"test": true}
  }'
```

## 🧪 Testing

### Run API Tests
```bash
python scripts/test_api.py
```

### Run Workflow Demo
```bash
python scripts/demo_workflow.py
```

### Manual Testing with Sample Data
```bash
# Test individual ticket creation
curl -X POST "http://localhost:8000/api/v1/tickets/" \
  -H "Content-Type: application/json" \
  -d @scripts/sample_ticket.json

# Test bulk creation
curl -X POST "http://localhost:8000/api/v1/tickets/bulk" \
  -H "Content-Type: application/json" \
  -d @scripts/sample_bulk_tickets.json
```

## 📊 Dashboard

Access the real-time dashboard at `http://localhost:8000/frontend/index.html`

Features:
- Real-time sentiment statistics
- Interactive charts showing sentiment distribution and trends
- Live ticket feed with sentiment indicators
- Auto-refresh every 30 seconds

## 🔧 Configuration

### Sentiment Thresholds
- **SENTIMENT_THRESHOLD**: Minimum negative sentiment score to trigger alerts (default: 0.3)
- **ALERT_COOLDOWN_MINUTES**: Time between alerts for the same channel/source (default: 15)

### Performance Settings
- **MAX_CONCURRENT_REQUESTS**: Maximum concurrent ticket processing (default: 10)
- **REQUEST_TIMEOUT_SECONDS**: Maximum processing time per request (default: 5)

### Slack Integration
- **SLACK_WEBHOOK_URL**: Incoming webhook URL for notifications
- **SLACK_CHANNEL**: Channel to send alerts to (default: #support-alerts)

## 📈 Performance

The system is optimized for:
- **Sub-5-second latency** for complete request-to-notification roundtrip
- **Efficient sentiment analysis** using lightweight NLP models
- **Async processing** for high throughput
- **Smart alert cooldowns** to prevent notification spam

### Performance Benchmarks
- **Sentiment Analysis**: ~50-200ms per ticket
- **Full Pipeline**: ~1-3 seconds per ticket (including database operations)
- **Bulk Processing**: ~2-5 tickets per second
- **Memory Usage**: ~50-100MB for typical workloads

## 🔍 Monitoring

### Logs
Logs are written to `logs/sentiment_watchdog.log` with configurable levels:
- **INFO**: General application events
- **DEBUG**: Detailed processing information
- **ERROR**: Error conditions and exceptions

### Health Checks
- **Basic Health**: `GET /health`
- **Detailed Health**: `GET /health/detailed` (includes component status)

### Metrics
The system tracks:
- Processing times per ticket
- Sentiment analysis accuracy
- Alert trigger rates
- Database performance
- Agent response times

## 🚨 Alert System

### Alert Types
- **Negative Sentiment**: When sentiment score < threshold
- **High Emotion**: When anger/frustration scores > 0.5
- **Urgent Priority**: When ticket priority is "urgent"

### Alert Severity
- **Critical**: Very negative sentiment (>0.7) or urgent tickets
- **High**: Negative sentiment (>0.5) or high emotion scores
- **Medium**: Moderate negative sentiment (>0.3)
- **Low**: Slight negative sentiment

### Slack Notifications
Alerts include:
- Ticket details and customer information
- Sentiment analysis results
- Response recommendations
- Direct links to ticket management

## 🔄 Development

### Project Structure
```
customer-sentiment-watchdog/
├── app/
│   ├── agents/              # AI agent implementations
│   ├── api/                 # FastAPI endpoints
│   ├── core/                # Configuration and database
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   └── main.py              # Application entry point
├── frontend/                # Dashboard HTML/CSS/JS
├── scripts/                 # Test and utility scripts
├── logs/                    # Application logs
└── requirements.txt         # Python dependencies
```

### Adding New Agents
1. Create agent class in `app/agents/`
2. Implement `initialize()`, `cleanup()`, and main processing methods
3. Register agent in `app/services/agent_manager.py`
4. Add configuration options in `app/core/config.py`

### Database Migrations
The system uses SQLAlchemy with automatic table creation. For production:
1. Use Alembic for migration management
2. Set up proper database backup procedures
3. Consider using PostgreSQL for high-volume deployments

## 🚀 Deployment

### Production Considerations
- **Database**: Use PostgreSQL for high-volume deployments
- **Caching**: Add Redis for session and trend caching
- **Load Balancing**: Use multiple FastAPI instances behind a load balancer
- **Monitoring**: Integrate with APM tools (e.g., Sentry, DataDog)
- **Security**: Add authentication and rate limiting

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "app.main"]
```

### Environment-Specific Configs
- **Development**: `DEBUG=true`, local SQLite
- **Staging**: `DEBUG=false`, PostgreSQL, Slack notifications disabled
- **Production**: `DEBUG=false`, PostgreSQL, full monitoring, rate limiting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test scripts for usage examples

---

**Built with ❤️ for customer support teams everywhere**