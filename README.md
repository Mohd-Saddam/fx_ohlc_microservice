# FX OHLC Microservice# FX OHLC Microservice - Production Ready



A high-performance, real-time foreign exchange (FX) tick data ingestion and OHLC aggregation service built with FastAPI, TimescaleDB, and Redis.**A high-performance, event-driven FastAPI microservice for real-time FX OHLC data processing**



## Table of Contents[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)

- [Overview](#overview)[![TimescaleDB](https://img.shields.io/badge/TimescaleDB-Latest-orange.svg)](https://www.timescale.com)

- [Features](#features)[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io)

- [Project Structure](#project-structure)

- [Prerequisites](#prerequisites)## Overview

- [Complete Setup & Testing Guide](#complete-setup--testing-guide)(#quick-start)
- [WebSocket Live Demo](#websocket-live-demo)
- [Environment Variables](#environment-variables)This microservice is a **production-ready solution** for ingesting, processing, and serving real-time FX (Foreign Exchange) OHLC (Open, High, Low, Close) data. Built with modern Python technologies and optimized for low-latency financial data streaming.

- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [WebSocket Streams](#websocket-streams)
- [Architecture](#architecture)
- [Production Deployment](#production-deployment)

## Overview

This microservice provides real-time FX tick data ingestion with automatic OHLC (Open, High, Low, Close) aggregation at multiple time intervals. It uses TimescaleDB's continuous aggregates for efficient time-series data processing and Redis Pub/Sub for event-driven tick distribution.

### Features

- **Real-time tick ingestion** at 1-second intervals
- **Automatic OHLC aggregation** (minute, hour, day)
- **Custom time boundaries** for daily aggregations 

- **WebSocket streaming** for live data feeds

- **RESTful API** for historical data queries**Requirement**: Provide minute, hourly, and daily OHLC that populates in real-time when users request data.

- **Production-ready** with Docker deployment

**Solution**:

## FeaturesTimescaleDB Continuous Aggregates with aggressive refresh policies:

- Minute OHLC: Refreshes every **5 seconds**

### Core Functionality- Hourly OHLC: Refreshes every **30 seconds**

- Daily OHLC: Refreshes every **5 minutes**

- **Tick Data Management**: Create, read, update, and delete individual tick records

- **Bulk Operations**: Efficient bulk tick insertionExample: EURUSD minute data from 5 PM to 6 PM returns 60 rows (05:00, 05:01, ..., 05:59) with real-time updates.

- **Real-time OHLC**: Minute, hourly, and daily OHLC with configurable refresh intervals

- **Custom Day Boundaries**: Define daily aggregations starting at any hour (e.g., 22:00 for FX markets)### Problem 2: Custom Day Boundaries (10 PM Start) 

- **WebSocket Streaming**: Live tick and OHLC data broadcasting

- **Data Compression**: Automatic TimescaleDB compression for historical data**Requirement**: Daily OHLC where the day starts at 22:00 (10 PM) instead of midnight.

- **Data Retention**: Configurable retention policies

**Solution**: 

### Technical FeaturesCustom PostgreSQL function using `time_bucket` with custom origin parameter. Supports any hour (0-23) as day start while maintaining 24-hour periods.



- **Event-Driven Architecture**: Redis Pub/Sub for decoupled tick processing---

- **Continuous Aggregates**: TimescaleDB automatic materialized views

- **Async I/O**: Full async/await support for high concurrency## Architecture
### High-Level System Diagram

```

�                           CLIENT APPLICATIONS                                �
�                                                                              �
�           �
�  �   Web App    �  �   Mobile     �  �   Trading    �  �   Analytics  �   �
�  �   Dashboard  �  �   Client     �  �   Platform   �  �   Tools      �   �
�  ��  ��  ��  ��   �
�         �                 �                  �                  �            �
�         ���            �
�                                    �                                         �
�                          HTTP/WebSocket (Port 8000)                          �
��
                                      �
�
�                        FASTAPI MICROSERVICE                                  �
�   �
�  �                         API LAYER                                      � �
�  �                      � �
�  �  � REST API     �  �  WebSocket   �  �   Health     �                � �
�  �  � Endpoints    �  �  Manager     �  �   Checks     �                � �
�  �  � /ticks       �  �  /ws/ticks   �  �  /health     �                � �
�  �  � /ohlc/*      �  �  /ws/ohlc/*  �  �  /ws/stats   �                � �
�  �  ��  ��  �                � �
�  ��� �
�            �                  �                                             �
�  �� �
�  �                      BUSINESS LOGIC LAYER                             � �
�  �                     � �
�  �  � OHLC Service �  � Tick Service �  �  Validation  �               � �
�  �  � (Aggregates) �  �  (CRUD)      �  �  (Pydantic)  �               � �
�  �  ��  ��  �               � �
�  ��� �
�            �                  �                                             �
�  �� �
�  �                     BACKGROUND SERVICES                               � �
�  �                                      � �
�  �  �Tick Generator���Redis Consumer�                           � �
�  �  �(1s interval) �  Pub/Sub�(DB Inserter) �                           � �
�  �  �         ��                           � �
�  �� �
��
                                          �
        �
        �                                 �                                 �
        �                                 �                                 �
                                   �
�  REDIS        �              �   TIMESCALEDB       �                     �
�  (Pub/Sub)    �              �   (PostgreSQL)      �                     �
�               �              �                     �                     �
�  �              �  �                     �
� � Channel:  � �              � �  Hypertable:    � �                     �
� � eurusd_   � �              � �  eurusd_ticks   � ��
� � ticks     � �              � �  (time, symbol, � �
� � �              � �   price)        � �
�               �              � �� �
�               �              �          �          �
�               �              � � �
�               �              � � Continuous      � �
�               �              � � Aggregates:     � �
�               �              � � � Minute (5s)   � �
�               �              � � � Hour (30s)    � �
�               �              � � � Day (5m)      � �
�               �              � � �
�              �

DATA FLOW:
1. Tick Generator � Redis Pub/Sub (eurusd_ticks channel)
2. Redis Consumer � Subscribes to channel � Inserts to TimescaleDB
3. TimescaleDB � Continuous Aggregates compute OHLC automatically
4. REST API � Queries TimescaleDB � Returns OHLC data
5. WebSocket � Broadcasts real-time updates to connected clients
```

- **Connection Pooling**: Optimized database connection management

- **Health Monitoring**: Built-in health check endpoints```

- **Comprehensive Testing**: Full test coverage with pytestCLIENT LAYER

 REST Clients (HTTP)

## Project Structure WebSocket Clients

 Web Dashboard

```

fx_ohlc_microservice/FASTAPI APPLICATION

 app/ REST API Endpoints (/ohlc/minute, /hour, /day, /custom-day)

�    __init__.py WebSocket Manager (/ws/ticks, /ws/ohlc/*)

�    main.py                 # FastAPI application entry point Business Logic & OHLC Service

�    config.py               # Configuration management Health Checks

�    database.py             # Database connection and session management

�    models.py               # SQLAlchemy ORM modelsDATA LAYER

�    schemas.py              # Pydantic request/response models TimescaleDB (PostgreSQL)

�    ingestion.py            # Tick data generator�    eurusd_ticks (hypertable)

�    redis_pubsub.py         # Redis publisher/subscriber�    eurusd_ohlc_minute (continuous aggregate, 5s refresh)

�    ohlc.py                 # OHLC API endpoints�    eurusd_ohlc_hour (continuous aggregate, 30s refresh)

�    websocket.py            # WebSocket connection manager�    eurusd_ohlc_day (continuous aggregate, 5m refresh)

�    timescale_setup.py      # TimescaleDB initialization Redis (Pub/Sub)

 tests/     eurusd_ticks channel

�    __init__.py

�    conftest.py             # Pytest fixtures and configurationINGESTION PIPELINE

�    test_tick_api.py        # CRUD API tests Tick Generator (1-second intervals)



 scripts/```

�    init_db.py              # Database initialization script

 docker-compose.yml          # Development environment---

 docker-compose.prod.yml     # Production environment

## Complete Setup & Testing Guide

### Prerequisites

Before starting, ensure you have:

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Git** for version control
- **Python** 3.10+ (for local development)
- **Ports available**: 8000 (API), 5432 (PostgreSQL), 6379 (Redis)

### Step-by-Step Setup

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd fx_ohlc_microservice
```

#### Step 2: Start All Services with Docker Compose

```bash
# Start all services in detached mode
docker-compose up -d

# Expected output:
# Creating network "fx_ohlc_microservice_default" with the default driver
# Creating fx_ohlc_microservice_db_1    ... done
# Creating fx_ohlc_microservice_redis_1 ... done
# Creating fx_ohlc_microservice_api_1   ... done
```

#### Step 3: Verify Services are Running

```bash
# Check all containers are up
docker-compose ps

# Expected output: All services should show "Up" status
# NAME                           STATUS
# fx_ohlc_microservice_api_1     Up (healthy)
# fx_ohlc_microservice_db_1      Up
# fx_ohlc_microservice_redis_1   Up
```

#### Step 4: Check Application Health

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected","redis":"connected"}
```

#### Step 5: Access API Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Step 6: View Live WebSocket Demo

Open your browser to:
- **WebSocket Test Page**: http://localhost:8000/ws-test

You should see:
- Real-time tick data streaming every second
- Live OHLC updates
- Connection statistics

### Testing the API

#### Test 1: Create a Single Tick

```bash
# Create a tick
curl -X POST "http://localhost:8000/ticks/" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "EURUSD",
    "time": "2025-12-05T10:00:00Z",
    "price": 1.0850
  }'

# Expected response (201 Created):
# {
#   "symbol": "EURUSD",
#   "time": "2025-12-05T10:00:00Z",
#   "price": 1.0850
# }
```

#### Test 2: Get Ticks by Time Range

```bash
# Query ticks
curl "http://localhost:8000/ticks/?symbol=EURUSD&start=2025-12-05T09:00:00Z&end=2025-12-05T11:00:00Z&limit=10"

# Expected response (200 OK):
# [
#   {
#     "symbol": "EURUSD",
#     "time": "2025-12-05T10:00:00Z",
#     "price": 1.0850
#   },
#   ...
# ]
```

#### Test 3: Bulk Create Ticks

```bash
# Create multiple ticks
curl -X POST "http://localhost:8000/ticks/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {"symbol": "EURUSD", "time": "2025-12-05T10:00:00Z", "price": 1.0850},
    {"symbol": "EURUSD", "time": "2025-12-05T10:00:01Z", "price": 1.0851},
    {"symbol": "EURUSD", "time": "2025-12-05T10:00:02Z", "price": 1.0852}
  ]'

# Expected response (201 Created):
# {"created": 3}
```

#### Test 4: Get Minute OHLC

```bash
# Get minute OHLC aggregates
curl "http://localhost:8000/ohlc/minute?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T11:00:00Z"

# Expected response (200 OK):
# [
#   {
#     "bucket": "2025-12-05T10:00:00Z",
#     "symbol": "EURUSD",
#     "open": 1.0850,
#     "high": 1.0875,
#     "low": 1.0845,
#     "close": 1.0860,
#     "tick_count": 60
#   },
#   ...
# ]
```

#### Test 5: Get Hourly OHLC

```bash
# Get hourly OHLC aggregates
curl "http://localhost:8000/ohlc/hour?symbol=EURUSD&start=2025-12-05T00:00:00Z&end=2025-12-05T23:59:59Z"
```

#### Test 6: Get Daily OHLC (Standard)

```bash
# Get daily OHLC (midnight to midnight)
curl "http://localhost:8000/ohlc/day?symbol=EURUSD&start=2025-12-01T00:00:00Z&end=2025-12-05T23:59:59Z"
```

#### Test 7: Get Custom Day OHLC (10 PM Start)

```bash
# Get daily OHLC starting at 22:00 (10 PM)
curl "http://localhost:8000/ohlc/custom-day?symbol=EURUSD&start=2025-12-01T00:00:00Z&end=2025-12-05T23:59:59Z&day_start_hour=22"
```

#### Test 8: Update a Tick

```bash
# Update tick price
curl -X PUT "http://localhost:8000/ticks/?symbol=EURUSD&time=2025-12-05T10:00:00Z" \
  -H "Content-Type: application/json" \
  -d '{"price": 1.0900}'

# Expected response (200 OK):
# {
#   "symbol": "EURUSD",
#   "time": "2025-12-05T10:00:00Z",
#   "price": 1.0900
# }
```

#### Test 9: Delete Ticks by Range

```bash
# Delete ticks in time range
curl -X DELETE "http://localhost:8000/ticks/?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T10:05:00Z"

# Expected response (200 OK):
# {"deleted": 5}
```

#### Test 10: WebSocket Connection Test

```javascript
// Connect to live tick stream
const ws = new WebSocket('ws://localhost:8000/ws/ticks/EURUSD');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Tick received:', data);
  // Output: {"time": "2025-12-05T...", "symbol": "EURUSD", "price": 1.0850}
};

ws.onopen = () => console.log('Connected to tick stream');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

### Running Unit Tests

```bash
# Activate virtual environment (if using local Python)
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Run all tests
pytest

# Expected output:
# ======================== test session starts =========================
# collected 19 items
# 
# tests/test_tick_api.py::TestTickAPI::test_create_single_tick PASSED [ 5%]
# tests/test_tick_api.py::TestTickAPI::test_create_tick_invalid_symbol PASSED [10%]
# ...
# ======================== 19 passed in 0.24s ==========================
```

### Run Tests with Verbose Output

```bash
# Detailed test output
pytest -v

# Expected output shows each test:
# tests/test_tick_api.py::TestTickAPI::test_create_single_tick PASSED
# tests/test_tick_api.py::TestTickAPI::test_bulk_create_ticks PASSED
# tests/test_tick_api.py::TestTickAPI::test_get_ticks_by_time_range PASSED
# ...
```

### Run Tests with Coverage

```bash
# Run with coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Verify System is Working

After setup, confirm everything is running:

```bash
# 1. Check Docker containers
docker-compose ps

# 2. Check application health
curl http://localhost:8000/health

# 3. View logs
docker-compose logs -f api

# 4. Check database
docker-compose exec db psql -U postgres -d fx_ohlc -c "SELECT COUNT(*) FROM eurusd_ticks;"

# 5. Check Redis
docker-compose exec redis redis-cli PING
# Expected: PONG

# 6. Run tests
pytest -v

# 7. Open WebSocket demo
open http://localhost:8000/ws-test
```

### Troubleshooting

**Port already in use:**
```bash
# Stop services and try again
docker-compose down
docker-compose up -d
```

**Database connection error:**
```bash
# Wait for database to be ready (takes ~10 seconds on first start)
docker-compose logs db
```

**Tests failing:**
```bash
# Ensure services are running
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up -d
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Next Steps

- Setup complete! System is running
-  Read [docs/SETUP.md](docs/SETUP.md) for detailed configuration
-  Read [docs/TESTING.md](docs/TESTING.md) for testing best practices
-  Explore API at http://localhost:8000/docs
-  Try WebSocket demo at http://localhost:8000/ws-test
## WebSocket Live Demo

Experience real-time data streaming with our interactive WebSocket demo:

**Demo URL**: [http://localhost:8000/ws-test](http://localhost:8000/ws-test)

![WebSocket Demo](docs/websocket-demo.png)

### Features:
- **Real-time Tick Data**: See live EURUSD prices updating every second
- **OHLC Streams**: Choose between Minute, Hourly, or Daily OHLC aggregations
- **Live Statistics**: Monitor average, min, and max prices in real-time
- **Connection Controls**: Connect, disconnect, and clear messages on demand

### How to Use:
1. Start the application: `docker-compose up -d`
2. Open your browser to [http://localhost:8000/ws-test](http://localhost:8000/ws-test)
3. Click **"Connect"** to start receiving live tick data
4. Switch between different OHLC endpoints using the buttons
5. Watch real-time financial data stream into your browser!

   docker-compose up -d## API Documentation

   ```

### REST Endpoints

3. **Verify services are healthy**:

   ```bash#### Minute OHLC (Real-time, 5-second refresh)

   curl http://localhost:8000/health```bash

   ```GET /ohlc/minute?start=2025-12-04T17:00:00Z&end=2025-12-04T18:00:00Z&symbol=EURUSD

```

4. **Access the API documentation**:

   Open http://localhost:8000/docs in your browserReturns 60 rows for each minute from 17:00 to 17:59:

```json

5. **View live WebSocket demo**:[

   Open http://localhost:8000/demo in your browser  {

    "bucket": "2025-12-04T17:00:00Z",

### Local Development Setup    "symbol": "EURUSD",

    "open": 1.0500,

1. **Create and activate virtual environment**:    "high": 1.0525,

   ```bash    "low": 1.0495,

   python3 -m venv venv    "close": 1.0510,

   source venv/bin/activate  # On Windows: venv\Scripts\activate    "tick_count": 60

   ```  },

  ...

2. **Install dependencies**:]

   ```bash```

   pip install -r requirements.txt

   pip install -r requirements-dev.txt#### Hourly OHLC (Real-time, 30-second refresh)

   ``````bash

GET /ohlc/hour?start=2025-12-03T00:00:00Z&end=2025-12-04T00:00:00Z

3. **Start infrastructure (database and Redis)**:```

   ```bash

   docker-compose up -d db redis#### Daily OHLC (Standard midnight-to-midnight)

   ``````bash

GET /ohlc/day?start=2025-12-01T00:00:00Z&end=2025-12-05T00:00:00Z

4. **Run the application**:```

   ```bash

   uvicorn app.main:app --reload#### Custom Day OHLC (10 PM day boundary)

   ``````bash

GET /ohlc/custom-day?start=2025-12-01T00:00:00Z&end=2025-12-05T00:00:00Z&day_start_hour=22

For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md).```



## Environment VariablesReturns daily OHLC where each day runs from 22:00 to 22:00 (24 hours).



Create a `.env` file in the project root (see `.env.example` for template):### WebSocket Endpoints



```envConnect to real-time streams:

# Database Configuration

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fx_ohlc```javascript

DB_POOL_SIZE=20// Live ticks (1-second updates)

DB_MAX_OVERFLOW=40ws://localhost:8000/ws/ticks



# Redis Configuration// Live minute OHLC (5-second updates)

REDIS_URL=redis://localhost:6379/0ws://localhost:8000/ws/ohlc/minute



# Application Configuration// Live hourly OHLC

LOG_LEVEL=INFOws://localhost:8000/ws/ohlc/hour

SYMBOL=EURUSD

DAY_START_HOUR=22// Live daily OHLC

ws://localhost:8000/ws/ohlc/day

# TimescaleDB Configuration```

COMPRESSION_AFTER_DAYS=7

RETENTION_DAYS=90**Demo Page**: http://localhost:8000/demo

```

---

### Key Configuration Options

##  Project Structure

| Variable | Description | Default |

|----------|-------------|---------|```

| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@db:5432/fx_ohlc` |fx_ohlc_microservice/

| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` | app/

| `SYMBOL` | FX pair to track | `EURUSD` |�    main.py              # FastAPI app + lifespan management

| `DAY_START_HOUR` | Hour when trading day starts (0-23) | `22` |�    config.py            # Pydantic settings

| `LOG_LEVEL` | Logging verbosity | `INFO` |�    database.py          # Async SQLAlchemy engine

| `DB_POOL_SIZE` | Database connection pool size | `20` |�    models.py            # Tick model (hypertable)

| `COMPRESSION_AFTER_DAYS` | Days before data compression | `7` |�    schemas.py           # Pydantic schemas

| `RETENTION_DAYS` | Days to retain data | `90` |�    ohlc.py              # OHLC REST endpoints

�    websocket.py         # WebSocket manager + endpoints

## Running the Application�    ingestion.py         # Tick generator

�    redis_pubsub.py      # Redis consumer

### Using Docker Compose�    timescale_setup.py   # Hypertables + continuous aggregates

 tests/

```bash�    conftest.py          # Pytest fixtures

# Start all services in detached mode�    test_tick_api.py  # Full OHLC test suite


 Dockerfile               # Production image

# View logs docker-compose.yml       # Local dev stack

docker-compose logs -f docker-compose.prod.yml  # Production stack

 requirements.txt         # Python dependencies

# View logs for specific service requirements-dev.txt     # Dev/test dependencies

docker-compose logs -f api README.md

```

# Stop all services

docker-compose down---



# Rebuild and restart##  Testing

docker-compose up --build -d

``````bash

# Run all tests

### Using Make Commandspytest tests/ -v



```bash# Run with coverage

# Start development environmentpytest tests/ -v --cov=app --cov-report=html

make docker-run

# Run specific test file

# View logspytest tests/test_tick_api.py -v

make logs```



# Stop services**Test Coverage**:

make docker-stop- All tick CRUD endpoints (create, read, update, delete)

- Bulk insert operations

# Run tests- Data validation and edge cases



# Format code- Time range queries and pagination
- Error handling and validation
make format

---

# Run linters

make lint## Production Deployment

```

### Environment Variables (.env)

### Manual Python Execution

```bash

```bash# Database

# Activate virtual environmentPOSTGRES_USER=postgres

source venv/bin/activatePOSTGRES_PASSWORD=<strong-password>

POSTGRES_HOST=db

# Run applicationPOSTGRES_DB=fxohlc

uvicorn app.main:app --host 0.0.0.0 --port 8000

# Redis

# Run with hot reload (development)REDIS_HOST=redis

uvicorn app.main:app --reloadREDIS_PORT=6379

```

# Application

## Running Tests

The project includes a comprehensive test suite covering all CRUD operations and API endpoints.

### Test Coverage

**19 CRUD API Tests** (All Passing ):

| Test Category | Tests | Description |
|---------------|-------|-------------|
| **CREATE** | 6 tests | Single tick, bulk insert, validation, duplicates |
| **READ** | 4 tests | Time range queries, pagination, limits |
| **UPDATE** | 2 tests | Price updates, non-existent ticks |
| **DELETE** | 4 tests | Range deletion, single delete, validation |
| **INTEGRATION** | 3 tests | Multi-symbol, large batches, timestamp precision |

### Running Tests

#### Quick Test (All Tests)

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Expected output:
# ======================== 19 passed in 0.28s =========================
```

#### Verbose Output

```bash
# Run with verbose output to see each test
pytest -v

# Sample output:
# tests/test_tick_api.py::TestTickAPI::test_create_single_tick PASSED           [ 5%]
# tests/test_tick_api.py::TestTickAPI::test_create_tick_invalid_symbol PASSED   [10%]
# tests/test_tick_api.py::TestTickAPI::test_create_tick_invalid_price PASSED    [15%]
# tests/test_tick_api.py::TestTickAPI::test_bulk_create_ticks PASSED            [21%]
# tests/test_tick_api.py::TestTickAPI::test_bulk_create_empty_list PASSED       [26%]
# tests/test_tick_api.py::TestTickAPI::test_get_ticks_by_time_range PASSED      [31%]
# tests/test_tick_api.py::TestTickAPI::test_get_ticks_with_limit PASSED         [36%]
# tests/test_tick_api.py::TestTickAPI::test_get_ticks_invalid_time_range PASSED [42%]
# tests/test_tick_api.py::TestTickAPI::test_update_tick_price PASSED            [47%]
# tests/test_tick_api.py::TestTickAPI::test_update_nonexistent_tick PASSED      [52%]
# tests/test_tick_api.py::TestTickAPI::test_delete_ticks_by_range PASSED        [57%]
# tests/test_tick_api.py::TestTickAPI::test_delete_ticks_invalid_range PASSED   [63%]
# tests/test_tick_api.py::TestTickAPI::test_delete_single_tick PASSED           [68%]
# tests/test_tick_api.py::TestTickAPI::test_delete_nonexistent_single_tick PASSED [73%]
# tests/test_tick_api.py::TestTickAPI::test_create_tick_duplicate PASSED        [78%]
# tests/test_tick_api.py::TestTickAPI::test_tick_api_with_different_symbols PASSED [84%]
# tests/test_tick_api.py::TestTickAPI::test_bulk_create_large_batch PASSED      [89%]
# tests/test_tick_api.py::TestTickAPI::test_get_ticks_pagination PASSED         [94%]
# tests/test_tick_api.py::TestTickAPI::test_tick_timestamp_precision PASSED     [100%]
```

#### Run Specific Tests

```bash
# Run only tick API tests
pytest tests/test_tick_api.py -v

# Run a specific test
pytest tests/test_tick_api.py::TestTickAPI::test_create_single_tick -v

# Run tests matching a pattern
pytest -k "create" -v  # Runs all tests with "create" in the name
```

#### Coverage Report

```bash
# Run with coverage
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

#### Using Make Commands

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run with detailed output
make test-verbose
```

### Test Results

Running `pytest -v` produces the following output:

```
========================= test session starts ==========================
platform darwin -- Python 3.12.9, pytest-7.4.3, pluggy-1.6.0
collected 19 items

tests/test_tick_api.py::TestTickAPI::test_create_single_tick PASSED        [ 5%]
tests/test_tick_api.py::TestTickAPI::test_create_tick_invalid_symbol PASSED [10%]
tests/test_tick_api.py::TestTickAPI::test_create_tick_invalid_price PASSED  [15%]
tests/test_tick_api.py::TestTickAPI::test_bulk_create_ticks PASSED          [21%]
tests/test_tick_api.py::TestTickAPI::test_bulk_create_empty_list PASSED     [26%]
tests/test_tick_api.py::TestTickAPI::test_get_ticks_by_time_range PASSED    [31%]
tests/test_tick_api.py::TestTickAPI::test_get_ticks_with_limit PASSED       [36%]
tests/test_tick_api.py::TestTickAPI::test_get_ticks_invalid_time_range PASSED [42%]
tests/test_tick_api.py::TestTickAPI::test_update_tick_price PASSED          [47%]
tests/test_tick_api.py::TestTickAPI::test_update_nonexistent_tick PASSED    [52%]
tests/test_tick_api.py::TestTickAPI::test_delete_ticks_by_range PASSED      [57%]
tests/test_tick_api.py::TestTickAPI::test_delete_ticks_invalid_range PASSED [63%]
tests/test_tick_api.py::TestTickAPI::test_delete_single_tick PASSED         [68%]
tests/test_tick_api.py::TestTickAPI::test_delete_nonexistent_single_tick PASSED [73%]
tests/test_tick_api.py::TestTickAPI::test_create_tick_duplicate PASSED      [78%]
tests/test_tick_api.py::TestTickAPI::test_tick_api_with_different_symbols PASSED [84%]
tests/test_tick_api.py::TestTickAPI::test_bulk_create_large_batch PASSED    [89%]
tests/test_tick_api.py::TestTickAPI::test_get_ticks_pagination PASSED       [94%]
tests/test_tick_api.py::TestTickAPI::test_tick_timestamp_precision PASSED   [100%]

======================== 19 passed in 0.28s ============================
```

### Individual Test Descriptions

| Test Name | Purpose |
|-----------|---------|
| `test_create_single_tick` | Verify single tick creation via POST /ticks/ |
| `test_create_tick_invalid_symbol` | Validate symbol field validation |
| `test_create_tick_invalid_price` | Validate price must be positive |
| `test_bulk_create_ticks` | Test bulk insertion of 5 ticks |
| `test_bulk_create_empty_list` | Verify empty list handling |
| `test_get_ticks_by_time_range` | Query ticks within time range |
| `test_get_ticks_with_limit` | Test pagination with limit parameter |
| `test_get_ticks_invalid_time_range` | Handle start > end gracefully |
| `test_update_tick_price` | Update existing tick price via PUT |
| `test_update_nonexistent_tick` | Verify 404 for non-existent tick |
| `test_delete_ticks_by_range` | Delete ticks within time range |
| `test_delete_ticks_invalid_range` | Handle invalid range deletion |
| `test_delete_single_tick` | Delete individual tick by time+symbol |
| `test_delete_nonexistent_single_tick` | Verify 404 for missing tick |
| `test_create_tick_duplicate` | Handle duplicate time+symbol |
| `test_tick_api_with_different_symbols` | Test multiple FX pairs |
| `test_bulk_create_large_batch` | Insert 100 ticks in one request |
| `test_get_ticks_pagination` | Test various limit values |
| `test_tick_timestamp_precision` | Verify microsecond precision |

### Prerequisites for Running Tests

```bash
# Ensure database and Redis are running
docker-compose up -d db redis

# Or start all services
docker-compose up -d

# Verify services are ready
docker-compose ps
```

For detailed testing documentation and best practices, see [docs/TESTING.md](docs/TESTING.md).



## API Documentation## Key Technical Decisions



### Interactive API Docs### Why TimescaleDB?

- **Hypertables**: Automatic partitioning by time

- **Swagger UI**: http://localhost:8000/docs- **Continuous Aggregates**: Pre-computed OHLC views

- **ReDoc**: http://localhost:8000/redoc- **Compression**: Automatic data compression

- **Retention**: Built-in data lifecycle management

### Main Endpoints- **PostgreSQL**: Full SQL support with time-series optimizations



#### Tick Data Management### Why Redis Pub/Sub?

- **Decoupling**: Generator and consumer are independent

```bash- **Scalability**: Multiple consumers can subscribe

# Create single tick- **Low Latency**: In-memory message passing

POST /ticks/- **Reliability**: At-least-once delivery

Content-Type: application/json

{### Why Event-Driven Architecture?

  "symbol": "EURUSD",- **Non-blocking**: Async I/O throughout

  "time": "2025-12-05T10:30:00Z",- **Scalability**: Horizontal scaling capability

  "price": 1.12345- **Real-time**: Immediate data propagation

}- **Resilience**: Component failures are isolated



# Bulk create ticks---

POST /ticks/bulk

Content-Type: application/json## Monitoring & Health

[

  {"symbol": "EURUSD", "time": "2025-12-05T10:30:00Z", "price": 1.12345},### Health Endpoints

  {"symbol": "EURUSD", "time": "2025-12-05T10:30:01Z", "price": 1.12346}

]```bash

# Application health

# Get ticks by time rangecurl http://localhost:8000/health

GET /ticks/?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T11:00:00Z&limit=1000

# WebSocket connection stats

# Update tick pricecurl http://localhost:8000/ws/stats

PUT /ticks/?symbol=EURUSD&time=2025-12-05T10:30:00Z```

Content-Type: application/json

{### Logs

  "price": 1.12350

}```bash

# All services

# Delete ticks by time rangedocker-compose logs -f

DELETE /ticks/?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T11:00:00Z

```# API only

docker-compose logs -f api

#### OHLC Data

# TimescaleDB

```bashdocker-compose logs -f db

# Get minute OHLC```

GET /ohlc/minute?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T11:00:00Z

---

# Get hourly OHLC

GET /ohlc/hour?symbol=EURUSD&start=2025-12-05T00:00:00Z&end=2025-12-05T23:59:59Z## Development Commands



# Get daily OHLC```bash

GET /ohlc/day?symbol=EURUSD&start=2025-12-01T00:00:00Z&end=2025-12-31T23:59:59Zmake help          # Show all commands

make install-dev   # Install dev dependencies

# Get custom daily OHLC (starting at 22:00)make test          # Run tests

GET /ohlc/custom-day?symbol=EURUSD&start=2025-12-01T00:00:00Z&end=2025-12-31T23:59:59Z&day_start_hour=22make test-cov      # Run tests with coverage

```make format        # Format code (black + isort)

make lint          # Run linters

#### Systemmake docker-build  # Build Docker image

make docker-run    # Start Docker Compose

```bash```

# Health check

GET /health---



# WebSocket statistics## Technical Implementation Details

GET /ws/stats

```### TimescaleDB Setup



### Response Format1. **Hypertable Creation**:

```sql

All tick CRUD endpoints return JSON arrays:SELECT create_hypertable(

    'eurusd_ticks',

```json    by_range('time'),

[    chunk_time_interval => INTERVAL '1 day'

  {);

    "bucket": "2025-12-05T10:30:00Z",```

    "symbol": "EURUSD",

    "open": 1.12340,2. **Continuous Aggregate (Minute OHLC)**:

    "high": 1.12380,```sql

    "low": 1.12320,CREATE MATERIALIZED VIEW eurusd_ohlc_minute

    "close": 1.12360,WITH (timescaledb.continuous) AS

    "tick_count": 60SELECT

  }    time_bucket('1 minute', time) AS bucket,

]    symbol,

```    first(price, time) AS open,

    max(price) AS high,

## WebSocket Streams    min(price) AS low,

    last(price, time) AS close,

### Available WebSocket Endpoints    count(*) AS tick_count

FROM eurusd_ticks

```javascriptGROUP BY bucket, symbol;

// Live tick stream```

const ws = new WebSocket('ws://localhost:8000/ws/ticks/EURUSD');

3. **Real-Time Refresh Policy**:

// Minute OHLC stream```sql

const ws = new WebSocket('ws://localhost:8000/ws/ohlc/minute/EURUSD');SELECT add_continuous_aggregate_policy(

    'eurusd_ohlc_minute',

// Hourly OHLC stream    start_offset => INTERVAL '1 hour',

const ws = new WebSocket('ws://localhost:8000/ws/ohlc/hour/EURUSD');    end_offset => INTERVAL '1 second',

    schedule_interval => INTERVAL '5 seconds'

// Daily OHLC stream);

const ws = new WebSocket('ws://localhost:8000/ws/ohlc/day/EURUSD');```

```

### Custom Day Function (Problem 2 Solution)

### WebSocket Demo Page

```sql

Visit http://localhost:8000/demo to see a live WebSocket demo with real-time tick and OHLC data streaming.CREATE FUNCTION get_custom_day_ohlc(

    start_time TIMESTAMPTZ,

## Architecture    end_time TIMESTAMPTZ,

    day_start_hour INT DEFAULT 22

### System Architecture)

RETURNS TABLE (...) AS $$

```BEGIN

    RETURN QUERY

�  Client Apps    �    SELECT

�  (Web/Mobile)   �        time_bucket('1 day', time, 

��            (DATE_TRUNC('day', start_time) + 

         � HTTP/WebSocket             INTERVAL '1 hour' * day_start_hour)

         �        ) AS bucket,

�        symbol,

�     FastAPI Application         �        first(price, time) AS open,

�     �        max(price) AS high,

�  �   REST API Endpoints     �   �        min(price) AS low,

�  �  /ticks, /ohlc/*        �   �        last(price, time) AS close,

�  �   �        count(*)::BIGINT AS tick_count

�     �    FROM eurusd_ticks

�  �  WebSocket Manager       �   �    WHERE time >= start_time AND time < end_time

�  �  /ws/ticks, /ws/ohlc/*  �   �    GROUP BY bucket, symbol

�  �   �    ORDER BY bucket ASC;

�     �END;

�  �  Background Services     �   �$$ LANGUAGE plpgsql;

�  �  - Tick Generator        �   �```

�  �  - Redis Consumer        �   �

�  �   �This function:

���- Uses `time_bucket` with custom origin for day boundaries

         �           �- Supports any hour (0-23) as day start

         �           �- Still aggregates full 24-hour periods

    �  �- Maintains correct OHLC calculation

    � Redis  �  � Postgres�

    � Pub/Sub�  �TimescaleDB---

    �  �

```## Requirements Checklist



### Data Flow### Technical Stack 

- [x] Python (FastAPI)

1. **Tick Generation**: Background service generates tick data every second- [x] PostgreSQL with TimescaleDB

2. **Publishing**: Ticks published to Redis Pub/Sub channel- [x] Redis (Pub/Sub)

3. **Consumption**: Redis consumer saves ticks to TimescaleDB- [x] Docker & Docker Compose

4. **Aggregation**: Continuous aggregates automatically compute OHLC- [x] WebSocket (real-time streaming)

5. **Streaming**: WebSocket manager broadcasts updates to connected clients- [x] REST API

6. **Queries**: REST API serves historical data from continuous aggregates- [x] Event-driven architecture



### Technologies### Features 

- [x] Low-latency data processing

- **FastAPI**: Modern async web framework- [x] Pub/Sub messaging (Redis)

- **TimescaleDB**: Time-series optimized PostgreSQL- [x] Time-series data handling

- **Redis**: In-memory data store for Pub/Sub- [x] Real-time OHLC aggregation

- **SQLAlchemy**: Async ORM for database interactions- [x] WebSocket live streaming

- **Pydantic**: Data validation and serialization- [x] Production-ready deployment

- **Uvicorn**: ASGI server- [x] Comprehensive testing

- **Docker**: Containerization

- **Nginx**: Reverse proxy and load balancing### Problem Solutions 

- [x] **Problem 1**: Real-time OHLC (minute/hour/day) with continuous aggregates

## Production Deployment- [x] **Problem 2**: Custom day boundaries (10 PM start) with time_bucket function



### Production Configuration---



Use `docker-compose.prod.yml` for production deployments:## About



```bashThis project demonstrates production-ready backend development skills:

docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

```- **Architecture Design**: Event-driven microservice architecture

- **Database Expertise**: TimescaleDB hypertables, continuous aggregates, optimization

### Key Production Features- **Real-Time Systems**: WebSocket streaming, Pub/Sub messaging

- **API Development**: FastAPI, async/await, Pydantic validation

- **Nginx reverse proxy** with rate limiting- **DevOps**: Docker, Docker Compose, health checks, monitoring

- **Resource limits** on all containers- **Testing**: Comprehensive async test suite

- **Health checks** for automatic recovery- **Performance**: Connection pooling, caching, compression

- **Restart policies** for fault tolerance- **Production Readiness**: Logging, error handling, graceful shutdown

- **Connection pooling** for database efficiency

- **Structured logging** for monitoring**Author**: Saddam  

- **Data compression** for storage optimization**Purpose**: Technical assessment for Backend Developer position

- **Retention policies** for data management

---

### Environment-Specific Settings

## Support

```bash

# ProductionFor questions or issues:

export LOG_LEVEL=WARNING1. Check API documentation: http://localhost:8000/docs

export DB_POOL_SIZE=502. Review logs: `docker-compose logs -f`

export DB_MAX_OVERFLOW=1003. Verify health: `curl http://localhost:8000/health`



# Development---

export LOG_LEVEL=DEBUG

export DB_POOL_SIZE=10

export DB_MAX_OVERFLOW=20
```

### Monitoring

```bash
# Check application health
curl http://localhost:8000/health

# View real-time logs
docker-compose logs -f api

# Check database performance
docker-compose exec db psql -U postgres -d fx_ohlc -c "SELECT * FROM timescaledb_information.jobs;"

curl http://localhost:8000/ws/stats
```

---

**For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md)**

**For testing documentation, see [docs/TESTING.md](docs/TESTING.md)**
