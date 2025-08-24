
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the FastAPI application
from app.main import app
from app.core.config import settings


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


def main():
    """Main application entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting Customer Sentiment Watchdog AI Agent System")

    # Verify required environment variables
    required_vars = ["GOOGLE_GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please check your .env file and ensure all required variables are set")
        # For testing, let's set a dummy key
        os.environ["GOOGLE_GEMINI_API_KEY"] = "dummy_key_for_testing"
        logger.info("Using dummy Gemini API key for testing")

    try:
        logger.info(f"Starting FastAPI server at http://{settings.HOST}:{settings.PORT}")
        logger.info("System ready for sentiment analysis!")
        logger.info("API Documentation available at /docs")

        # Import and run uvicorn
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info"
        )

    except Exception as e:
        logger.error(f"Fatal error starting system: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

