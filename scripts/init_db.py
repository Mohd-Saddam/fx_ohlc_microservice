"""Database initialization script."""

import asyncio
import logging
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import init_db
from app.timescale_setup import setup_timescaledb, setup_custom_day_aggregate
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Initialize database and TimescaleDB setup."""
    try:
        logger.info("Starting database initialization...")
        
        # Initialize database tables
        logger.info("Creating database tables...")
        await init_db()
        logger.info("Database tables created successfully")
        
        # Initialize TimescaleDB setup
        logger.info("Setting up TimescaleDB hypertables and continuous aggregates...")
        await setup_timescaledb()
        logger.info("TimescaleDB setup completed successfully")
        
        # Initialize custom day aggregate function
        logger.info("Setting up custom day OHLC function...")
        await setup_custom_day_aggregate()
        logger.info("Custom day OHLC function created successfully")
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())