# Testing Guide

This document describes the testing strategy, test structure, and how to run tests for the FX OHLC Microservice.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)

## Overview

The project uses `pytest` as the testing framework with full support for async tests. The test suite covers:

- **Tick API** (CRUD operations)
- **OHLC API** (time-series aggregations)
- **WebSocket connections** (real-time streaming)
- **Integration tests** (end-to-end workflows)

### Testing Philosophy

- **Comprehensive**: Test all API endpoints and edge cases
- **Isolated**: Each test is independent and can run alone
- **Fast**: Tests complete in seconds using real database
- **Realistic**: Uses actual TimescaleDB, not mocks
- **Maintainable**: Clear test names and well-organized structure

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
└── test_tick_api.py         # Tick CRUD operations (19 tests)
```

### Test Organization

Tests are organized by API functionality:

**test_tick_api.py** - Tick Data Management (19 tests)
- Create operations (single, bulk, validation)
- Read operations (time ranges, limits, pagination)
- Update operations (price modifications)
- Delete operations (single, ranges)
- Edge cases (duplicates, invalid data)

## Running Tests

### Prerequisites

Ensure the testing infrastructure is running:

```bash
# Start database and Redis
docker-compose up -d db redis

# Or start all services
docker-compose up -d
```

### Quick Test

Run all tests with default settings:

```bash
# Activate virtual environment (if running locally)
source venv/bin/activate

# Run all tests
pytest

# Expected output:
# ============================= test session starts ==============================
# collected 33 items
#
# tests/test_tick_api.py::TestTickAPI::test_create_single_tick PASSED     [  3%]
# tests/test_tick_api.py::TestTickAPI::test_bulk_create_ticks PASSED      [  6%]
# ...
# ============================== 33 passed in 12.34s ==============================
```

### Verbose Output

```bash
# Run with verbose output to see each test name
pytest -v

# Run with very verbose output (shows test details)
pytest -vv

# Show print statements
pytest -v -s
```

### Run Specific Tests

```bash
# Run single test file
pytest tests/test_tick_api.py

# Run single test class
pytest tests/test_tick_api.py::TestTickAPI

# Run single test function
pytest tests/test_tick_api.py::TestTickAPI::test_create_single_tick

# Run tests matching pattern
pytest -k "test_create"  # Runs all tests with "create" in name
pytest -k "tick_api or ohlc"  # Runs tick_api OR ohlc tests
```

### Test Output Control

```bash
# Short test summary (show only failures)
pytest --tb=short

# No traceback (clean output)
pytest --tb=no

# Show slowest tests
pytest --durations=10

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (auto-detect CPU cores)
pytest -n auto

# Run on specific number of workers
pytest -n 4
```

## Test Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Report Example

```bash
pytest --cov=app --cov-report=term-missing

# Output:
# ---------- coverage: platform darwin, python 3.10.0 -----------
# Name                         Stmts   Miss  Cover   Missing
# ----------------------------------------------------------
# app/__init__.py                  0      0   100%
# app/config.py                   15      0   100%
# app/database.py                 25      2    92%   45-46
# app/ingestion.py                48      3    94%   67-69
# app/main.py                    120      5    96%   234-238
# app/models.py                   18      0   100%
# app/ohlc.py                     75      2    97%   123-124
# app/redis_pubsub.py             55      4    93%   89-92
# app/schemas.py                  25      0   100%
# app/timescale_setup.py          95      3    97%   156-158
# app/websocket.py                68      5    93%   145-149
# ----------------------------------------------------------
# TOTAL                          544     24    96%
```

### Using Make

```bash
# Run tests
make test

# Run with coverage
make test-cov

# Run and open coverage report
make coverage
```

## Writing Tests

### Test Structure

All tests follow this pattern:

```python
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone

class TestExampleAPI:
    """Test suite for Example API endpoints."""
    
    @pytest.mark.asyncio
    async def test_example_endpoint(self, async_client: AsyncClient):
        """Test description in imperative mood."""
        # Arrange: Prepare test data
        test_data = {
            "symbol": "EURUSD",
            "price": 1.12345
        }
        
        # Act: Make API call
        response = await async_client.post("/endpoint", json=test_data)
        
        # Assert: Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["symbol"] == "EURUSD"
```

### Using Fixtures

Fixtures are defined in `conftest.py` and are automatically available to all tests:

```python
@pytest.mark.asyncio
async def test_with_fixtures(
    self, 
    async_client: AsyncClient,      # HTTP client
    sample_tick_data: dict,          # Sample tick
    sample_bulk_ticks: list          # Sample bulk ticks
):
    # Fixtures are automatically injected
    response = await async_client.post("/ticks/", json=sample_tick_data)
    assert response.status_code == 201
```

### Available Fixtures

| Fixture | Type | Description |
|---------|------|-------------|
| `async_client` | AsyncClient | HTTP client for API calls |
| `sample_tick_data` | dict | Single tick with current timestamp |
| `sample_bulk_ticks` | list | 5 ticks with sequential timestamps |
| `ohlc_time_range` | tuple | (start, end) datetime tuple |

### Testing Async Code

All tests that interact with the API must be async:

```python
@pytest.mark.asyncio  # Required for async tests
async def test_async_endpoint(self, async_client):
    # Use await for async operations
    response = await async_client.get("/endpoint")
    assert response.status_code == 200
```

### Testing Error Cases

```python
@pytest.mark.asyncio
async def test_invalid_input(self, async_client):
    """Test API handles invalid input correctly."""
    invalid_data = {"price": -1.0}  # Negative price is invalid
    
    response = await async_client.post("/ticks/", json=invalid_data)
    
    assert response.status_code == 422  # Validation error
    data = response.json()
    assert "detail" in data
```

### Testing URL Encoding

When testing endpoints with datetime parameters, ensure proper URL encoding:

```python
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_datetime_params(self, async_client):
    """Test endpoint with datetime URL parameters."""
    start = datetime.now(timezone.utc)
    
    # URL encode the '+' in timezone (+00:00 -> %2B00:00)
    start_encoded = start.isoformat().replace('+', '%2B')
    
    response = await async_client.get(f"/endpoint?start={start_encoded}")
    assert response.status_code == 200
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: timescale/timescaledb:latest-pg14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: fx_ohlc
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/fx_ohlc
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

Install pre-commit hooks to run tests before committing:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
EOF

# Install hooks
pre-commit install
```

## Troubleshooting

### Common Issues

**Problem**: Tests fail with "database connection error"

```bash
# Ensure database is running
docker-compose ps db

# Check database is ready
docker-compose exec db pg_isready

# Restart database
docker-compose restart db
```

**Problem**: Tests fail with "Redis connection error"

```bash
# Ensure Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Restart Redis
docker-compose restart redis
```

**Problem**: "No module named 'app'"

```bash
# Ensure you're in the project root directory
pwd
# Should end with: /fx_ohlc_microservice

# Ensure virtual environment is activated
which python
# Should show: /path/to/fx_ohlc_microservice/venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem**: Tests hang or take too long

```bash
# Run with timeout
pytest --timeout=30

# Check for hanging database connections
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Restart all services
docker-compose restart
```

**Problem**: URL encoding test failures

```bash
# Ensure timestamps are properly encoded
# Bad:  start=2025-12-05T10:00:00+00:00
# Good: start=2025-12-05T10:00:00%2B00:00

# Update tests to use .replace('+', '%2B')
```

### Test Data Cleanup

Tests automatically clean up data, but if needed:

```bash
# Reset database
docker-compose down -v
docker-compose up -d

# Or manually truncate tables
docker-compose exec db psql -U postgres -d fx_ohlc -c "TRUNCATE TABLE eurusd_ticks;"
```

### Debugging Tests

```bash
# Run with Python debugger
pytest --pdb

# Drop into debugger on failure
pytest --pdb --maxfail=1

# Show local variables on failure
pytest -l

# Very verbose output
pytest -vv -s
```

### Performance Profiling

```bash
# Install pytest-profiling
pip install pytest-profiling

# Profile tests
pytest --profile

# Profile and sort by cumulative time
pytest --profile --profile-svg
```

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
   - Good: `test_create_tick_with_invalid_price_returns_422`
   - Bad: `test_tick_error`

2. **Test Independence**: Each test should be self-contained
   - Don't rely on test execution order
   - Clean up test data in fixtures

3. **Async Tests**: Always mark async tests with `@pytest.mark.asyncio`

4. **Assertions**: Use specific assertions
   - Good: `assert response.status_code == 201`
   - Bad: `assert response`

5. **Edge Cases**: Test boundary conditions
   - Empty lists
   - Maximum values
   - Invalid input
   - Missing parameters

6. **Documentation**: Add docstrings to test classes and functions

7. **Coverage**: Aim for >90% code coverage, but focus on meaningful tests

---

**For more information**: See [README.md](README.md) for general documentation and [SETUP.md](SETUP.md) for installation instructions.
