"""
Main application entry point
"""
import logging
from typing import Optional

from .config import config


def setup_logging(level: str = "INFO") -> None:
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )


def create_app():
    """Create and configure the main application"""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Initializing Google Trends Website Builder")
    
    # Application initialization will be implemented in later tasks
    logger.info(f"Database URL: {config.database.url}")
    logger.info(f"Redis URL: {config.redis.url}")
    logger.info(f"API will run on {config.api.host}:{config.api.port}")
    
    return None  # Placeholder for actual app instance


if __name__ == "__main__":
    app = create_app()
    print("Google Trends Website Builder - Foundation Setup Complete")
    print("Run 'python -m src.api.main' to start the API server")
    print("Run 'streamlit run src/web/dashboard.py' to start the web dashboard")