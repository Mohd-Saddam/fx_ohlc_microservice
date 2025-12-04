"""
FastAPI application for FX OHLC tick data ingestion and aggregation.

Main application providing:
- Real-time tick data ingestion via Redis Pub/Sub
- CRUD operations for tick management
- Automatic OHLC aggregation using TimescaleDB continuous aggregates
- WebSocket streaming for live data feeds
- Production-ready health checks and monitoring
- Prometheus metrics for observability
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator
from app.config import settings
from app.database import init_db, close_db
from app.timescale_setup import setup_timescaledb, setup_custom_day_aggregate
from app.ohlc import router as ohlc_router
from app.tick_api import router as tick_router
from app.websocket import router as websocket_router, manager
from app.ws_test import router as ws_test_router
from app.ingestion import tick_generator
from app.redis_pubsub import tick_consumer
from app.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting FX OHLC Microservice...")
    
    # Initialize database
    await init_db()
    
    # Set up TimescaleDB
    await setup_timescaledb()
    await setup_custom_day_aggregate()
    
    # Start background tasks
    consumer_task = asyncio.create_task(start_consumer())
    generator_task = asyncio.create_task(start_generator())
    ws_redis_task = asyncio.create_task(start_websocket_redis())
    ws_ohlc_task = asyncio.create_task(start_websocket_ohlc())
    
    logger.info("Application started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    tick_consumer.running = False
    tick_generator.running = False
    consumer_task.cancel()
    generator_task.cancel()
    ws_redis_task.cancel()
    ws_ohlc_task.cancel()
    await manager.shutdown()
    await close_db()
    logger.info("Shutdown complete")


async def start_consumer():
    """Start Redis tick consumer."""
    try:
        await tick_consumer.connect()
        await tick_consumer.consume_ticks()
    except Exception as e:
        logger.error(f"Consumer failed: {e}")


async def start_generator():
    """Start tick generator."""
    try:
        await tick_generator.connect()
        await tick_generator.generate_ticks()
    except Exception as e:
        logger.error(f"Generator failed: {e}")


async def start_websocket_redis():
    """Start WebSocket Redis listener."""
    try:
        await manager.start_redis_listener()
    except Exception as e:
        logger.error(f"WebSocket Redis listener failed: {e}")


async def start_websocket_ohlc():
    """Start WebSocket OHLC streamer."""
    try:
        await manager.start_ohlc_streamer()
    except Exception as e:
        logger.error(f"WebSocket OHLC streamer failed: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers - CQRS Implementation
# =====================================
# WRITE SIDE (Command):
#   - tick_router: POST/PUT/DELETE for manual tick management
#   - Background tasks: Redis Pub/Sub ingestion (high throughput)
# READ SIDE (Query):
#   - ohlc_router: GET-only OHLC queries (real-time aggregates)
#   - websocket_router: Real-time streaming
app.include_router(ohlc_router)  # READ: OHLC queries
app.include_router(tick_router)  # WRITE: POST/PUT/DELETE tick management
app.include_router(websocket_router)  # READ: Real-time streaming
app.include_router(ws_test_router)  # Utility: WebSocket test page


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        database="connected",
        redis="connected",
        version=settings.API_VERSION
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        database="connected",
        redis="connected",
        version=settings.API_VERSION
    )


@app.get("/demo", response_class=HTMLResponse)
async def websocket_demo():
    """WebSocket demo page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FX OHLC WebSocket Demo</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 { 
                color: white; 
                text-align: center; 
                margin-bottom: 30px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            .grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
                gap: 20px; 
            }
            .panel { 
                background: white; 
                padding: 25px; 
                border-radius: 12px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            }
            .panel:hover { transform: translateY(-5px); }
            h2 { 
                color: #333; 
                font-size: 20px; 
                margin-bottom: 15px;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }
            . data { 
                font-family: 'Courier New', monospace; 
                background: #f8f9fa; 
                padding: 15px; 
                border-left: 4px solid #4CAF50; 
                margin: 15px 0;
                border-radius: 4px;
                max-height: 200px;
                overflow-y: auto;
                font-size: 13px;
                line-height: 1.6;
            }
            .status { 
                padding: 8px 16px; 
                border-radius: 20px; 
                display: inline-block;
                font-weight: 600;
                font-size: 14px;
                margin-bottom: 15px;
            }
            .connected { background: #4CAF50; color: white; }
            .disconnected { background: #f44336; color: white; }
            .controls { margin: 15px 0; }
            button { 
                padding: 12px 24px; 
                margin: 5px; 
                cursor: pointer; 
                background: #667eea; 
                color: white; 
                border: none; 
                border-radius: 6px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            button:hover { 
                background: #5568d3;
                transform: scale(1.05);
            }
            button:active { transform: scale(0.95); }
            .price { font-size: 24px; font-weight: bold; color: #667eea; }
            .label { color: #666; font-size: 12px; text-transform: uppercase; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>FX OHLC WebSocket Demo - Real-Time Data Streaming</h1>
            
            <div class="grid">
                <div class="panel">
                    <h2>Real-Time Ticks</h2>
                    <span id="tick-status" class="status disconnected">Disconnected</span>
                    <div class="controls">
                        <button onclick="connectTicks()">▶ Connect</button>
                        <button onclick="disconnectTicks()">⏹ Disconnect</button>
                    </div>
                    <div id="tick-data" class="data">Waiting for data...</div>
                </div>
                
                <div class="panel">
                    <h2>Minute OHLC</h2>
                    <span id="minute-status" class="status disconnected">Disconnected</span>
                    <div class="controls">
                        <button onclick="connectMinute()">▶ Connect</button>
                        <button onclick="disconnectMinute()">⏹ Disconnect</button>
                    </div>
                    <div id="minute-data" class="data">Waiting for data...</div>
                </div>
                
                <div class="panel">
                    <h2>Hourly OHLC</h2>
                    <span id="hour-status" class="status disconnected">Disconnected</span>
                    <div class="controls">
                        <button onclick="connectHour()">▶ Connect</button>
                        <button onclick="disconnectHour()">⏹ Disconnect</button>
                    </div>
                    <div id="hour-data" class="data">Waiting for data...</div>
                </div>
                
                <div class="panel">
                    <h2>Daily OHLC</h2>
                    <span id="day-status" class="status disconnected">Disconnected</span>
                    <div class="controls">
                        <button onclick="connectDay()">▶ Connect</button>
                        <button onclick="disconnectDay()">⏹ Disconnect</button>
                    </div>
                    <div id="day-data" class="data">Waiting for data...</div>
                </div>
            </div>
        </div>
        
        <script>
            let tickWs, minuteWs, hourWs, dayWs;
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            
            function connectTicks() {
                tickWs = new WebSocket(`${protocol}//${host}/ws/ticks`);
                tickWs.onopen = () => {
                    document.getElementById('tick-status').className = 'status connected';
                    document.getElementById('tick-status').textContent = 'Connected ✓';
                };
                tickWs.onmessage = (event) => {
                    const data = JSON.parse(event. data);
                    document.getElementById('tick-data').innerHTML = 
                        `<div class="price">${data.price}</div>` +
                        `<div class="label">Symbol: ${data.symbol}</div>` +
                        `<div class="label">Time: ${new Date(data.time).toLocaleString()}</div>`;
                };
                tickWs.onclose = () => {
                    document.getElementById('tick-status').className = 'status disconnected';
                    document.getElementById('tick-status').textContent = 'Disconnected ✗';
                };
            }
            
            function disconnectTicks() {
                if (tickWs) tickWs.close();
            }
            
            function connectMinute() {
                minuteWs = new WebSocket(`${protocol}//${host}/ws/ohlc/minute`);
                minuteWs.onopen = () => {
                    document. getElementById('minute-status').className = 'status connected';
                    document.getElementById('minute-status'). textContent = 'Connected ✓';
                };
                minuteWs.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    document.getElementById('minute-data').innerHTML = formatOHLC(data);
                };
                minuteWs.onclose = () => {
                    document.getElementById('minute-status').className = 'status disconnected';
                    document.getElementById('minute-status').textContent = 'Disconnected ✗';
                };
            }
            
            function disconnectMinute() {
                if (minuteWs) minuteWs.close();
            }
            
            function connectHour() {
                hourWs = new WebSocket(`${protocol}//${host}/ws/ohlc/hour`);
                hourWs.onopen = () => {
                    document.getElementById('hour-status').className = 'status connected';
                    document. getElementById('hour-status').textContent = 'Connected ✓';
                };
                hourWs.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    document.getElementById('hour-data').innerHTML = formatOHLC(data);
                };
                hourWs.onclose = () => {
                    document.getElementById('hour-status').className = 'status disconnected';
                    document.getElementById('hour-status').textContent = 'Disconnected ✗';
                };
            }
            
            function disconnectHour() {
                if (hourWs) hourWs.close();
            }
            
            function connectDay() {
                dayWs = new WebSocket(`${protocol}//${host}/ws/ohlc/day`);
                dayWs. onopen = () => {
                    document.getElementById('day-status').className = 'status connected';
                    document.getElementById('day-status').textContent = 'Connected ✓';
                };
                dayWs.onmessage = (event) => {
                    const data = JSON. parse(event.data);
                    document.getElementById('day-data').innerHTML = formatOHLC(data);
                };
                dayWs.onclose = () => {
                    document.getElementById('day-status').className = 'status disconnected';
                    document.getElementById('day-status').textContent = 'Disconnected ✗';
                };
            }
            
            function disconnectDay() {
                if (dayWs) dayWs.close();
            }
            
            function formatOHLC(data) {
                return `
                    <div class="label">Bucket: ${new Date(data.bucket).toLocaleString()}</div>
                    <div><strong>O:</strong> ${data.open?. toFixed(5) || 'N/A'} | 
                    <strong>H:</strong> ${data.high?.toFixed(5) || 'N/A'} | 
                    <strong>L:</strong> ${data. low?.toFixed(5) || 'N/A'} | 
                    <strong>C:</strong> ${data.close?. toFixed(5) || 'N/A'}</div>
                    <div class="label">Ticks: ${data.tick_count || 0}</div>
                    <div class="label">Symbol: ${data.symbol}</div>
                `;
            }
        </script>
    </body>
    </html>
    """