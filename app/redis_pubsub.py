"""
Redis Pub/Sub consumer for tick data ingestion.

Subscribes to Redis tick channel and persists incoming tick data to TimescaleDB.
Uses INSERT ON CONFLICT for idempotent writes to handle duplicates safely.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from redis import asyncio as aioredis
from sqlalchemy import text
from app.config import settings
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def publish_tick(tick_data: dict):
    """
    Publish a tick to Redis channel for WebSocket streaming.
    
    Args:
        tick_data: Dictionary with 'time', 'symbol', 'price' keys
    """
    try:
        redis_client = await aioredis.from_url(
            settings.redis_url_with_auth,
            decode_responses=True,
            encoding="utf-8"
        )
        await redis_client.publish(settings.TICK_CHANNEL, json.dumps(tick_data))
        await redis_client.close()
    except Exception as e:
        logger.error(f"Failed to publish tick to Redis: {e}")


class RedisTickConsumer:
    """Consumer for tick data from Redis pub/sub."""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        self.running = False
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = await aioredis.from_url(
                settings.redis_url_with_auth,
                decode_responses=True,
                encoding="utf-8"
            )
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(settings.TICK_CHANNEL)
            logger.info(f"Subscribed to Redis channel: {settings.TICK_CHANNEL}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def consume_ticks(self):
        """Consume ticks from Redis and insert into database."""
        self.running = True
        logger.info("Starting tick consumer...")
        
        try:
            async for message in self.pubsub.listen():
                if not self.running:
                    break
                
                if message["type"] == "message":
                    try:
                        tick_data = json.loads(message["data"])
                        await self._insert_tick(tick_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in tick: {e}")
                    except Exception as e:
                        logger. error(f"Error processing tick: {e}")
        except Exception as e:
            logger. error(f"Consumer error: {e}")
        finally:
            await self.disconnect()
    
    async def _insert_tick(self, tick_data: dict):
        """Insert tick into database."""
        async with AsyncSessionLocal() as session:
            try:
                # Parse timestamp string to datetime if needed
                time_value = tick_data["time"]
                if isinstance(time_value, str):
                    time_value = datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                
                # Use INSERT ... ON CONFLICT for idempotency
                stmt = text("""
                    INSERT INTO eurusd_ticks (time, symbol, price)
                    VALUES (:time, :symbol, :price)
                    ON CONFLICT (time, symbol) DO UPDATE 
                    SET price = EXCLUDED.price
                """)
                
                await session.execute(stmt, {
                    "time": time_value,
                    "symbol": tick_data.get("symbol", "EURUSD"),
                    "price": tick_data["price"]
                })
                await session.commit()
                logger.debug(f"Inserted tick: {tick_data}")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error inserting tick: {e}")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        self.running = False
        if self.pubsub:
            await self.pubsub.unsubscribe(settings.TICK_CHANNEL)
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client. close()
        logger.info("Disconnected from Redis")


# Global consumer instance
tick_consumer = RedisTickConsumer()