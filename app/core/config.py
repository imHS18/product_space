"""
Configuration settings for the Customer Sentiment Watchdog system
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Customer Sentiment Watchdog"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./sentiment_watchdog.db",
        env="DATABASE_URL"
    )
    
    # AI/LLM
    GOOGLE_GEMINI_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_GEMINI_API_KEY")
    
    # Slack Integration
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    SLACK_CHANNEL: str = Field(default="#support-alerts", env="SLACK_CHANNEL")
    
    # Sentiment Analysis
    SENTIMENT_ANALYSIS_ENABLED: bool = Field(default=True, env="SENTIMENT_ANALYSIS_ENABLED")
    SENTIMENT_THRESHOLD: float = Field(default=0.3, env="SENTIMENT_THRESHOLD")
    ALERT_THRESHOLD: float = Field(default=0.3, env="ALERT_THRESHOLD")
    ALERT_COOLDOWN_MINUTES: int = Field(default=15, env="ALERT_COOLDOWN_MINUTES")
    SLACK_COOLDOWN_MINUTES: int = Field(default=15, env="SLACK_COOLDOWN_MINUTES")
    
    # Performance
    MAX_CONCURRENT_REQUESTS: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    REQUEST_TIMEOUT_SECONDS: int = Field(default=5, env="REQUEST_TIMEOUT_SECONDS")
    MAX_PROCESSING_TIME: int = Field(default=5, env="MAX_PROCESSING_TIME")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/sentiment_watchdog.log", env="LOG_FILE")
    
    # Cache
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    CACHE_TTL_SECONDS: int = Field(default=300, env="CACHE_TTL_SECONDS")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()
