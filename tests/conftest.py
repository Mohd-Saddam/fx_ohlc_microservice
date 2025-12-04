"""Test configuration and fixtures for pytest."""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator

from app.main import app
from app.database import get_db
from app.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def sample_tick_data():
    """Sample tick data for testing."""
    return {
        "symbol": "EURUSD",
        "time": datetime.now(timezone.utc).isoformat(),
        "price": 1.12345
    }


@pytest.fixture
def sample_bulk_ticks():
    """Sample bulk tick data for testing."""
    base_time = datetime.now(timezone.utc)
    return [
        {
            "symbol": "EURUSD",
            "time": (base_time + timedelta(seconds=i)).isoformat(),
            "price": 1.12345 + (i * 0.00001)
        }
        for i in range(5)
    ]


@pytest.fixture
def ohlc_time_range():
    """Standard time range for OHLC queries."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=1)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "symbol": "EURUSD"
    }


@pytest.fixture
def custom_day_params():
    """Parameters for custom day OHLC queries."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=7)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "day_start_hour": 22,
        "symbol": "EURUSD"
    }

    """Sample OHLC data for tests."""
    return {
        "symbol": "EURUSD",
        "timeframe": "1h",
        "timestamp": "2023-01-01T12:00:00",
        "open_price": 1.0500,
        "high_price": 1.0550,
        "low_price": 1.0450,
        "close_price": 1.0525,
        "volume": 1000,
        "tick_count": 50
    }


@pytest.fixture
def sample_ohlc_update():
    """Sample OHLC update data for tests."""
    return {
        "open_price": 1.0510,
        "high_price": 1.0560,
        "low_price": 1.0460,
        "close_price": 1.0535,
        "volume": 1100,
        "tick_count": 55
    }