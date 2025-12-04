"""
Database connection and session management.

Configures async SQLAlchemy engine with connection pooling for TimescaleDB.
"""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

# Async engine with connection pooling for high concurrency
# pool_pre_ping: Validates connections before use to prevent stale connection errors
# jit=off: Disables JIT compilation in PostgreSQL for faster query execution
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=settings.DB_POOL_RECYCLE,
    connect_args={
        "server_settings": {"jit": "off"}
    }
)

# Session factory for creating database sessions
# expire_on_commit=False: Keeps objects accessible after commit
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Automatically handles session lifecycle (creation, commit/rollback, cleanup).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    # Import models to register them with Base.metadata
    from app import models  # noqa: F401
    
    async with engine.begin() as conn:
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")