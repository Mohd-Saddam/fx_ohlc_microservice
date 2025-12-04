"""
WebSocket endpoints for real-time tick and OHLC streaming.

Manages WebSocket connections and broadcasts live data updates from Redis
to connected clients for real-time dashboards and monitoring.
"""
import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis import asyncio as aioredis
from app.config import settings
from app. database import AsyncSessionLocal
from app.schemas import ConnectionStatsResponse
from sqlalchemy import text

logger = logging. getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections for broadcasting."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "ticks": set(),
            "ohlc_minute": set(),
            "ohlc_hour": set(),
            "ohlc_day": set(),
        }
        self.redis_client = None
        self.pubsub = None
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Accept and register WebSocket connection."""
        await websocket.accept()
        if channel in self.active_connections:
            self.active_connections[channel]. add(websocket)
            logger.info(f"Client connected to {channel}.  Total: {len(self.active_connections[channel])}")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove WebSocket connection."""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.info(f"Client disconnected from {channel}.  Total: {len(self.active_connections[channel])}")
    
    async def broadcast(self, message: dict, channel: str):
        """Broadcast message to all connected clients on a channel."""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections[channel].discard(conn)
    
    async def start_redis_listener(self):
        """Listen to Redis pub/sub and broadcast to WebSocket clients."""
        try:
            self.redis_client = await aioredis.from_url(
                settings.redis_url_with_auth,
                decode_responses=True,
                encoding="utf-8"
            )
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(settings.TICK_CHANNEL)
            
            logger.info("WebSocket Redis listener started")
            
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        tick_data = json.loads(message["data"])
                        # Broadcast to tick subscribers
                        await self.broadcast(tick_data, "ticks")
                    except Exception as e:
                        logger. error(f"Error broadcasting tick: {e}")
        except Exception as e:
            logger.error(f"Redis listener error: {e}")
    
    async def start_ohlc_streamer(self):
        """Stream OHLC updates periodically."""
        logger.info("OHLC streamer started")
        
        while True:
            try:
                # Fetch latest minute OHLC
                minute_data = await self._fetch_latest_ohlc("minute", 1)
                if minute_data:
                    await self.broadcast(minute_data, "ohlc_minute")
                
                # Fetch latest hourly OHLC
                hour_data = await self._fetch_latest_ohlc("hour", 1)
                if hour_data:
                    await self. broadcast(hour_data, "ohlc_hour")
                
                # Fetch latest daily OHLC
                day_data = await self._fetch_latest_ohlc("day", 1)
                if day_data:
                    await self. broadcast(day_data, "ohlc_day")
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in OHLC streamer: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_latest_ohlc(self, interval: str, limit: int = 1) -> dict:
        """Fetch latest OHLC data from database."""
        table_map = {
            "minute": "eurusd_ohlc_minute",
            "hour": "eurusd_ohlc_hour",
            "day": "eurusd_ohlc_day"
        }
        
        table = table_map.get(interval)
        if not table:
            return None
        
        async with AsyncSessionLocal() as session:
            try:
                stmt = text(f"""
                    SELECT bucket, symbol, open, high, low, close, tick_count
                    FROM {table}
                    ORDER BY bucket DESC
                    LIMIT :limit
                """)
                
                result = await session.execute(stmt, {"limit": limit})
                row = result.fetchone()
                
                if row:
                    return {
                        "interval": interval,
                        "bucket": row[0]. isoformat(),
                        "symbol": row[1],
                        "open": row[2],
                        "high": row[3],
                        "low": row[4],
                        "close": row[5],
                        "tick_count": row[6],
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
            except Exception as e:
                logger.error(f"Error fetching latest OHLC: {e}")
        
        return None
    
    async def shutdown(self):
        """Cleanup on shutdown."""
        if self.pubsub:
            await self. pubsub.unsubscribe(settings.TICK_CHANNEL)
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("WebSocket manager shut down")


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ticks")
async def websocket_ticks(websocket: WebSocket):
    """
    WebSocket endpoint for real-time tick data.
    
    Client receives JSON messages:
    {
        "time": "2025-12-03T12:34:56. 789Z",
        "symbol": "EURUSD",
        "price": 1.10045
    }
    """
    await manager.connect(websocket, "ticks")
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "ticks")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "ticks")


@router.websocket("/ohlc/minute")
async def websocket_ohlc_minute(websocket: WebSocket):
    """
    WebSocket endpoint for real-time minute OHLC data.
    Updates every 5 seconds with latest minute bar. 
    """
    await manager. connect(websocket, "ohlc_minute")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "ohlc_minute")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "ohlc_minute")


@router.websocket("/ohlc/hour")
async def websocket_ohlc_hour(websocket: WebSocket):
    """
    WebSocket endpoint for real-time hourly OHLC data. 
    Updates every 5 seconds with latest hour bar. 
    """
    await manager.connect(websocket, "ohlc_hour")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "ohlc_hour")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "ohlc_hour")


@router.websocket("/ohlc/day")
async def websocket_ohlc_day(websocket: WebSocket):
    """
    WebSocket endpoint for real-time daily OHLC data. 
    Updates every 5 seconds with latest day bar.
    """
    await manager.connect(websocket, "ohlc_day")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager. disconnect(websocket, "ohlc_day")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "ohlc_day")


@router.get("/stats", response_model=ConnectionStatsResponse)
async def websocket_stats():
    """Get WebSocket connection statistics."""
    return ConnectionStatsResponse(
        connections={
            channel: len(connections)
            for channel, connections in manager.active_connections.items()
        },
        total=sum(len(conns) for conns in manager. active_connections.values()),
        timestamp=datetime.now(timezone.utc)
    )