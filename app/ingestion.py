"""
Tick data generation and publishing to Redis Pub/Sub.

Simulates FX market data for testing and demonstration purposes.
In production, replace with real market data feed integration.
"""
import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone
from redis import asyncio as aioredis
from app.config import settings
from app.metrics import (
    ticks_ingested_total,
    redis_messages_published,
    background_task_duration,
    background_task_errors
)

logger = logging.getLogger(__name__)


class TickGenerator:
    """Generates simulated EURUSD tick data."""
    
    def __init__(self, initial_price: float = 1.10000):
        self.price = initial_price
        self.redis_client = None
        self. running = False
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = await aioredis.from_url(
                settings.redis_url_with_auth,
                decode_responses=True,
                encoding="utf-8"
            )
            logger.info("Connected to Redis for tick publishing")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def generate_ticks(self):
        """Generate and publish ticks every second."""
        self.running = True
        logger.info("Starting tick generator...")
        
        try:
            while self.running:
                tick = self._create_tick()
                await self._publish_tick(tick)
                await asyncio.sleep(1)  # 1-second interval
        except Exception as e:
            logger.error(f"Tick generator error: {e}")
        finally:
            await self. disconnect()
    
    def _create_tick(self) -> dict:
        """Create a single tick with random price movement."""
        # Simulate realistic FX price movement
        change = random.uniform(-0.0005, 0.0005)
        self.price += change
        
        # Keep price in realistic range
        self.price = max(0.5, min(2.0, self.price))
        
        tick = {
            "time": datetime. now(timezone.utc).isoformat(),
            "symbol": "EURUSD",
            "price": round(self.price, 5)
        }
        return tick
    
    async def _publish_tick(self, tick: dict):
        """Publish tick to Redis channel."""
        start_time = time.time()
        try:
            await self.redis_client.publish(
                settings. TICK_CHANNEL,
                json.dumps(tick)
            )
            
            # Update metrics
            ticks_ingested_total.labels(symbol=tick['symbol']).inc()
            redis_messages_published.labels(channel=settings.TICK_CHANNEL).inc()
            
            logger.debug(f"Published tick: {tick}")
        except Exception as e:
            logger. error(f"Error publishing tick: {e}")
            background_task_errors.labels(task_name='tick_publisher').inc()
        finally:
            duration = time.time() - start_time
            background_task_duration.labels(task_name='tick_publisher').observe(duration)
    
    async def disconnect(self):
        """Disconnect from Redis."""
        self.running = False
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Disconnected tick generator from Redis")


# Global generator instance
tick_generator = TickGenerator()