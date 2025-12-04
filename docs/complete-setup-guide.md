## 🚀 Complete Setup & Testing Guide

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

- ✅ Setup complete! System is running
- 📖 Read [docs/SETUP.md](docs/SETUP.md) for detailed configuration
- 🧪 Read [docs/TESTING.md](docs/TESTING.md) for testing best practices
- 🔍 Explore API at http://localhost:8000/docs
- 🌐 Try WebSocket demo at http://localhost:8000/ws-test
