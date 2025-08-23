
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import agent initialization functions
from agents.orchestrator import create_orchestrator_agent
from agents.sentiment_analyst import create_sentiment_agent
from agents.alert_manager import create_alert_agent
from agents.response_generator import create_response_agent
from agents.integration_coordinator import create_integration_agent

# Import Crew orchestration and Flask app creation
from workflows.agent_crew import SentimentWatchdogCrew
from web.app import create_flask_app
from tools.database_manager import DatabaseManager


def setup_logging():
    """Configure logging for the application"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "sentiment_watchdog.log"),
            logging.StreamHandler()
        ]
    )


def initialize_agents():
    """Initialize all AI agents with their personalities and tools"""
    logger = logging.getLogger(__name__)
    logger.info("🤖 Initializing AI Agent System...")

    # Create individual agents
    orchestrator = create_orchestrator_agent()
    sentiment_analyst = create_sentiment_agent()
    alert_manager = create_alert_agent()
    response_generator = create_response_agent()
    integration_coordinator = create_integration_agent()

    logger.info("✅ All agents initialized successfully")

    return {
        "orchestrator": orchestrator,
        "sentiment_analyst": sentiment_analyst,
        "alert_manager": alert_manager,
        "response_generator": response_generator,
        "integration_coordinator": integration_coordinator
    }


def main():
    """Main application entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Starting Customer Sentiment Watchdog AI Agent System")

    # Verify required environment variables
    required_vars = ["OPENAI_API_KEY", "SLACK_WEBHOOK_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        logger.error("Please check your .env file and ensure all required variables are set")
        return 1

    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        logger.info("📊 Database initialized")

        # Initialize AI agents
        agents = initialize_agents()

        # Create agent crew for collaboration
        crew = SentimentWatchdogCrew(agents)
        logger.info("👥 Agent crew assembled")

        # Create and start Flask web application
        app = create_flask_app(crew)

        # Get configuration from environment
        host = os.getenv("FLASK_HOST", "0.0.0.0")
        port = int(os.getenv("FLASK_PORT", 5000))
        debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

        logger.info(f"🌐 Starting web server at http://{host}:{port}")
        logger.info("🎯 System ready for sentiment analysis!")

        # Start the application
        app.run(host=host, port=port, debug=debug)

    except Exception as e:
        logger.error(f"💥 Fatal error starting system: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

