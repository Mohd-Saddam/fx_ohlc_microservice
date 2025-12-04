# FX OHLC Microservice - Production Ready

A high-performance, event-driven FastAPI microservice for real-time FX OHLC data processing.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-Latest-orange.svg)](https://www.timescale.com)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation Methods](#installation-methods)
  - [Docker Setup (Recommended)](#docker-setup-recommended)
  - [Local Development Setup](#local-development-setup)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Monitoring](#monitoring)
  - [Prometheus & Grafana](#prometheus--grafana)
  - [Available Metrics](#available-metrics)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Test Coverage](#test-coverage)
  - [Writing Tests](#writing-tests)
- [API Documentation](#api-documentation)
- [WebSocket Streams](#websocket-streams)
- [WebSocket Live Demo](#websocket-live-demo)
- [Project Structure](#project-structure)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

## Overview

This microservice is a **production-ready solution** for ingesting, processing, and serving real-time FX (Foreign Exchange) OHLC (Open, High, Low, Close) data. Built with modern Python technologies and optimized for low-latency financial data streaming.

### Problem 1: Real-time OHLC Population

**Requirement**: Provide minute, hourly, and daily OHLC that populates in real-time when users request data.

**Solution**: TimescaleDB Continuous Aggregates with aggressive refresh policies:
- Minute OHLC: Refreshes every **5 seconds**
- Hourly OHLC: Refreshes every **30 seconds**
- Daily OHLC: Refreshes every **5 minutes**

Example: EURUSD minute data from 5 PM to 6 PM returns 60 rows (05:00, 05:01, ..., 05:59) with real-time updates.

### Problem 2: Custom Day Boundaries (10 PM Start)

**Requirement**: Daily OHLC where the day starts at 22:00 (10 PM) instead of midnight.

**Solution**: Custom PostgreSQL function using `time_bucket` with custom origin parameter. Supports any hour (0-23) as day start while maintaining 24-hour periods.

## Features

### Core Functionality

- **Tick Data Management**: Create, read, update, and delete individual tick records
- **Bulk Operations**: Efficient bulk tick insertion
- **Real-time OHLC**: Minute, hourly, and daily OHLC with configurable refresh intervals
- **Custom Day Boundaries**: Define daily aggregations starting at any hour (e.g., 22:00 for FX markets)
- **WebSocket Streaming**: Live tick and OHLC data broadcasting
- **Data Compression**: Automatic TimescaleDB compression for historical data
- **Data Retention**: Configurable retention policies

### Technical Features

- **Event-Driven Architecture**: Redis Pub/Sub for decoupled tick processing
- **Continuous Aggregates**: TimescaleDB automatic materialized views
- **Async I/O**: Full async/await support for high concurrency
- **Schema Validation**: Pydantic models for request/response validation
- **OpenAPI Documentation**: Interactive API docs at `/docs`
- **Health Checks**: Comprehensive health monitoring endpoints
- **Docker Support**: Full containerization with Docker Compose

## Architecture

For the complete architecture diagram and detailed explanation, see [docs/architecture-diagram.md](docs/architecture-diagram.md).

### Data Flow

1. **Tick Ingestion**:
   - Background task generates ticks every 1 second
   - POST `/ticks/` endpoint receives tick data
   - Tick stored in `eurusd_ticks` hypertable
   - Tick published to Redis `tick_created` channel

2. **OHLC Aggregation**:
   - TimescaleDB continuous aggregates automatically compute OHLC
   - Refresh policies keep aggregates up-to-date
   - Custom day boundary function handles 22:00 start time

3. **Data Consumption**:
   - REST API queries continuous aggregates for historical OHLC
   - WebSocket clients subscribe to Redis channel for real-time ticks
   - Both methods provide low-latency data access

### Technology Stack

- **FastAPI**: Modern Python web framework with async support
- **TimescaleDB**: Time-series database built on PostgreSQL
- **Redis**: In-memory data store for Pub/Sub messaging
- **Pydantic**: Data validation using Python type annotations
- **SQLAlchemy**: SQL toolkit and ORM
- **pytest**: Testing framework with async support
- **Docker**: Containerization and deployment

## Prerequisites

### Required Software

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| Docker | 20.10+ | Container runtime |
| Docker Compose | 2.0+ | Multi-container orchestration |
| Python | 3.10+ | Application runtime (local dev) |
| Git | 2.0+ | Version control |

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB free space

**Recommended**:
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 20+ GB free space (for data storage)

### Operating System Support

- **Linux**: Ubuntu 20.04+, Debian 11+, CentOS 8+
- **macOS**: 11+ (Big Sur or later)
- **Windows**: 10/11 with WSL2

## Quick Start

The fastest way to get started (requires Docker):

```bash
# Clone the repository
git clone <repository-url>
cd fx_ohlc_microservice

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check health
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs
```

That's it! The application is now running with sample data.

For detailed setup instructions, see [docs/complete-setup-guide.md](docs/complete-setup-guide.md).

## Installation Methods

Choose one of the following installation methods:

1. **Docker Setup** (Recommended) - Fastest and easiest, no Python setup required
2. **Local Development Setup** - For active development with hot reload

For complete installation instructions for both methods, see [docs/SETUP.md](docs/SETUP.md).

### Docker Setup (Recommended)

```bash
# Install Docker (if not already installed)
# See docs/SETUP.md for platform-specific instructions

# Clone repository
git clone <repository-url>
cd fx_ohlc_microservice

# Start all services
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

### Local Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scriptsctivate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start infrastructure (database and Redis only)
docker-compose up -d db redis

# Run application with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Setup

The database is automatically initialized when the application starts. It creates:

1. `eurusd_ticks` TimescaleDB hypertable
2. Continuous aggregates (minute, hour, day)
3. Refresh policies for real-time updates
4. Compression and retention policies

### Custom Day Boundary Implementation

The daily OHLC uses a custom PostgreSQL function for 22:00 (10 PM) start time:

```sql
CREATE MATERIALIZED VIEW eurusd_ohlc_day
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day'::interval, time, 
                TIMESTAMPTZ '2000-01-01 22:00:00+00') AS bucket,
    symbol,
    first(price, time) AS open,
    max(price) AS high,
    min(price) AS low,
    last(price, time) AS close,
    count(*) AS tick_count
FROM eurusd_ticks
GROUP BY bucket, symbol;
```

Returns daily OHLC where each day runs from 22:00 to 22:00 (24 hours).

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fx_ohlc
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://redis:6379/0

# Application
LOG_LEVEL=INFO
SYMBOL=EURUSD
DAY_START_HOUR=22

# TimescaleDB
COMPRESSION_AFTER_DAYS=7
RETENTION_DAYS=90
```

For local development, use `localhost` instead of service names in connection strings.

## Running the Application

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Using Make Commands

```bash
# Start services
make up

# View logs
make logs

# Stop services
make down

# Run tests
make test
```

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Monitoring

The microservice includes a complete monitoring stack with Prometheus and Grafana.

### Prometheus & Grafana

All monitoring services start automatically with Docker Compose:

```bash
# Start all services (includes monitoring)
docker-compose up -d
```

**Access URLs**:
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus UI**: http://localhost:9090
- **API Metrics**: http://localhost:8000/metrics

**Pre-configured Dashboard** includes:
- Request rate and latency (P95)
- Tick ingestion rate
- Database and Redis connections
- WebSocket connections
- Error rates

### Available Metrics

**Application Metrics**:
```promql
# Tick ingestion rate
rate(ticks_ingested_total[1m])

# OHLC query latency (P95)
histogram_quantile(0.95, rate(ohlc_query_duration_seconds_bucket[5m]))

# Active WebSocket connections
websocket_connections_active
```

**Infrastructure Metrics**:
```promql
# Database connections
pg_stat_database_numbackends{datname="fxohlc"}

# Redis clients
redis_connected_clients

# Request latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

For complete monitoring documentation, see [docs/MONITORING.md](docs/MONITORING.md) and [MONITORING_QUICKSTART.md](MONITORING_QUICKSTART.md).

## Testing

The project uses `pytest` with full async support. All tests run against real TimescaleDB and Redis instances.

For complete testing documentation, see [docs/TESTING.md](docs/TESTING.md).

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
└── test_tick_api.py         # Tick CRUD operations (19 tests)
```

### Running Tests

```bash
# Ensure infrastructure is running
docker-compose up -d db redis

# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_tick_api.py::TestTickAPI::test_create_single_tick

# Verbose output
pytest -v

# Show print statements
pytest -v -s
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open report
open htmlcov/index.html
```

Current coverage: **96%** (544/544 statements, 24 miss)

### Writing Tests

All tests follow the Arrange-Act-Assert pattern with async/await:

```python
import pytest
from httpx import AsyncClient

class TestTickAPI:
    @pytest.mark.asyncio
    async def test_create_single_tick(self, async_client: AsyncClient):
        # Arrange
        test_data = {"symbol": "EURUSD", "price": 1.12345}
        
        # Act
        response = await async_client.post("/ticks/", json=test_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["symbol"] == "EURUSD"
```

## API Documentation

### Interactive Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Create Tick**:
```bash
curl -X POST "http://localhost:8000/ticks/"   -H "Content-Type: application/json"   -d '{"symbol": "EURUSD", "price": 1.12345, "time": "2025-12-05T10:00:00Z"}'
```

**Get Ticks**:
```bash
curl "http://localhost:8000/ticks/?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T11:00:00Z"
```

**Get Minute OHLC**:
```bash
curl "http://localhost:8000/ohlc/minute?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T11:00:00Z"
```

**Get Hourly OHLC**:
```bash
curl "http://localhost:8000/ohlc/hour?symbol=EURUSD&start=2025-12-05T00:00:00Z&end=2025-12-05T23:59:59Z"
```

**Get Daily OHLC** (22:00 start):
```bash
curl "http://localhost:8000/ohlc/day?symbol=EURUSD&start=2025-12-01T22:00:00Z&end=2025-12-05T22:00:00Z"
```

### Key Technical Decisions

1. **CQRS Pattern**: Separate write (tick API) and read (OHLC API) sides
2. **Event-Driven**: Redis Pub/Sub decouples ingestion from broadcasting
3. **Continuous Aggregates**: Materialized views instead of on-demand computation
4. **Aggressive Refresh**: 5s/30s/5m refresh for real-time data
5. **Custom Time Buckets**: Flexible day boundaries via PostgreSQL functions

## WebSocket Streams

### JavaScript Client Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ticks');

ws.onmessage = (event) => {
  const tick = JSON.parse(event.data);
  console.log('New tick:', tick);
};
```

### Python Client Example

```python
import asyncio
import websockets
import json

async def subscribe_to_ticks():
    uri = "ws://localhost:8000/ws/ticks"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            tick = json.loads(message)
            print(f"Received tick: {tick}")

asyncio.run(subscribe_to_ticks())
```

## WebSocket Live Demo

The microservice includes a built-in WebSocket demo page.

### Accessing the Demo

```
http://localhost:8000/ws-test

```

<img width="1374" height="833" alt="websocket-demo" src="https://github.com/user-attachments/assets/64ad4650-f557-48cd-b068-aff8f78c50ab" />


### Demo Features

- Live tick data updates every second
- OHLC data refreshing automatically
- Connection status indicator
- Error handling and reconnection

### Demo Screenshot
check also websocket image 👇🏻

<img width="1374" height="833" alt="websocket-demo" src="https://github.com/user-attachments/assets/64ad4650-f557-48cd-b068-aff8f78c50ab" />


The demo shows:
- Current tick price and timestamp
- Latest minute, hourly, and daily OHLC bars
- Connection status

## Project Structure

```
fx_ohlc_microservice/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration and environment variables
│   ├── database.py         # Database connection and session management
│   ├── ingestion.py        # Background tick generator
│   ├── main.py             # FastAPI application entry point
│   ├── models.py           # SQLAlchemy models
│   ├── ohlc.py             # OHLC API endpoints (read side)
│   ├── redis_pubsub.py     # Redis Pub/Sub consumer
│   ├── schemas.py          # Pydantic validation models
│   ├── timescale_setup.py  # TimescaleDB initialization
│   └── websocket.py        # WebSocket endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   └── test_tick_api.py    # Tick API tests (19 tests)
├── docs/
│   ├── README.md           # Documentation index
│   ├── SETUP.md            # Detailed setup instructions
│   ├── TESTING.md          # Testing guide
│   ├── architecture-diagram.md  # System architecture
│   └── complete-setup-guide.md  # Step-by-step setup
├── scripts/
│   └── init_db.py          # Database initialization
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore patterns
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Application container
├── Makefile                # Convenience commands
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md               # This file
```

### Key Files Explained

**Configuration**:
- `app/config.py`: Loads environment variables
- `.env.example`: Template for configuration

**Database**:
- `app/database.py`: SQLAlchemy async engine and sessions
- `app/models.py`: ORM models for `eurusd_ticks`
- `app/timescale_setup.py`: Hypertables and continuous aggregates

**API**:
- `app/main.py`: FastAPI application with all routers
- `app/ohlc.py`: OHLC read API (minute, hour, day)
- `app/tick_api.py`: Tick write API (CRUD operations)
- `app/schemas.py`: Pydantic request/response models

**Real-time**:
- `app/ingestion.py`: Background tick generator
- `app/redis_pubsub.py`: Redis Pub/Sub consumer
- `app/websocket.py`: WebSocket broadcasting

## Production Deployment

### Using Docker Compose (Production)

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale api=4
```

### Environment Variables for Production

```env
# Use managed services for database and Redis
DATABASE_URL=postgresql+asyncpg://user:pass@db-host:5432/fx_ohlc
REDIS_URL=redis://:password@redis-host:6379/0

# Increase connection pools
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=100

# Set appropriate log level
LOG_LEVEL=WARNING
```

### Health Monitoring

```bash
# Health check
curl http://localhost:8000/health

# Check database connections
docker-compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

### Performance Tuning

**Database**:
```sql
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET shared_buffers = '4GB';
SELECT pg_reload_conf();
```

**Application**:
```bash
# Run with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Troubleshooting

### Container Issues

**Problem**: Docker containers won't start

```bash
# Check Docker is running
docker ps

# View logs
docker-compose logs api
docker-compose logs db

# Restart
docker-compose restart
```

**Problem**: Port already in use

```bash
# Find process
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.yml
```

### Database Issues

**Problem**: Cannot connect to database

```bash
# Check database is running
docker-compose ps db

# Verify connection
docker-compose exec db pg_isready -U postgres
```

**Problem**: OHLC data not updating

```bash
# Check refresh policies
docker-compose exec db psql -U postgres -d fx_ohlc -c   "SELECT view_name, refresh_interval FROM timescaledb_information.continuous_aggregate_stats;"

# Manual refresh
docker-compose exec db psql -U postgres -d fx_ohlc -c   "CALL refresh_continuous_aggregate('eurusd_ohlc_minute', NULL, NULL);"
```

### Application Issues

**Problem**: No tick data appearing

```bash
# Check tick generator logs
docker-compose logs api | grep "Publishing tick"

# Should see messages every second
```

**Problem**: WebSocket connection fails

```bash
# Test WebSocket
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket"   http://localhost:8000/ws/ticks
```

### Getting Help

If issues persist:

1. Check logs: `docker-compose logs -f`
2. Verify `.env` configuration
3. Try fresh start: `docker-compose down -v && docker-compose up -d`
4. See [docs/SETUP.md](docs/SETUP.md) and [docs/TESTING.md](docs/TESTING.md)

## Support

For questions and issues:

- **Documentation**: See `docs/` folder for detailed guides
- **API Docs**: http://localhost:8000/docs

---

**License**: MIT License

**Version**: 1.0.0
