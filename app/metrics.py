"""
Prometheus metrics for FX OHLC microservice.

Provides custom metrics for monitoring:
- Tick ingestion rate
- OHLC query performance
- WebSocket connections
- Database operations
- Redis pub/sub messages
"""
from prometheus_client import Counter, Histogram, Gauge, Info

# Application info
app_info = Info('fx_ohlc_app', 'FX OHLC Microservice Information')
app_info.info({
    'version': '1.0.0',
    'environment': 'production'
})

# Tick ingestion metrics
ticks_ingested_total = Counter(
    'ticks_ingested_total',
    'Total number of ticks ingested',
    ['symbol']
)

ticks_ingestion_duration = Histogram(
    'ticks_ingestion_duration_seconds',
    'Time spent ingesting ticks',
    ['symbol']
)

bulk_ticks_ingested_total = Counter(
    'bulk_ticks_ingested_total',
    'Total number of ticks ingested via bulk operations',
    ['symbol']
)

# OHLC query metrics
ohlc_queries_total = Counter(
    'ohlc_queries_total',
    'Total number of OHLC queries',
    ['interval', 'symbol']
)

ohlc_query_duration = Histogram(
    'ohlc_query_duration_seconds',
    'Time spent querying OHLC data',
    ['interval', 'symbol'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

ohlc_rows_returned = Histogram(
    'ohlc_rows_returned',
    'Number of OHLC rows returned',
    ['interval', 'symbol'],
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 5000]
)

# WebSocket metrics
websocket_connections = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections',
    ['endpoint']
)

websocket_messages_sent = Counter(
    'websocket_messages_sent_total',
    'Total number of WebSocket messages sent',
    ['endpoint', 'message_type']
)

websocket_errors = Counter(
    'websocket_errors_total',
    'Total number of WebSocket errors',
    ['endpoint', 'error_type']
)

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query execution time',
    ['operation', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Current database connection pool size'
)

db_connection_pool_available = Gauge(
    'db_connection_pool_available',
    'Available connections in the pool'
)

# Redis pub/sub metrics
redis_messages_published = Counter(
    'redis_messages_published_total',
    'Total number of Redis messages published',
    ['channel']
)

redis_messages_received = Counter(
    'redis_messages_received_total',
    'Total number of Redis messages received',
    ['channel']
)

redis_pubsub_duration = Histogram(
    'redis_pubsub_duration_seconds',
    'Time spent in Redis pub/sub operations',
    ['operation']
)

# TimescaleDB specific metrics
continuous_aggregate_refresh_duration = Histogram(
    'continuous_aggregate_refresh_duration_seconds',
    'Time spent refreshing continuous aggregates',
    ['aggregate_name']
)

hypertable_chunks = Gauge(
    'hypertable_chunks_total',
    'Total number of chunks in hypertable',
    ['hypertable']
)

compressed_chunks = Gauge(
    'compressed_chunks_total',
    'Total number of compressed chunks',
    ['hypertable']
)

# API endpoint metrics (supplementing prometheus-fastapi-instrumentator)
api_requests_in_progress = Gauge(
    'api_requests_in_progress',
    'Number of API requests currently being processed',
    ['method', 'endpoint']
)

# Error metrics
application_errors_total = Counter(
    'application_errors_total',
    'Total number of application errors',
    ['error_type', 'component']
)

# Background task metrics
background_task_duration = Histogram(
    'background_task_duration_seconds',
    'Time spent in background tasks',
    ['task_name']
)

background_task_errors = Counter(
    'background_task_errors_total',
    'Total number of background task errors',
    ['task_name']
)

# Data quality metrics
duplicate_ticks_rejected = Counter(
    'duplicate_ticks_rejected_total',
    'Total number of duplicate ticks rejected',
    ['symbol']
)

invalid_ticks_rejected = Counter(
    'invalid_ticks_rejected_total',
    'Total number of invalid ticks rejected',
    ['symbol', 'reason']
)

# Performance metrics
tick_processing_lag = Gauge(
    'tick_processing_lag_seconds',
    'Lag between tick creation and processing',
    ['symbol']
)

ohlc_data_freshness = Gauge(
    'ohlc_data_freshness_seconds',
    'Age of the most recent OHLC data',
    ['interval', 'symbol']
)
