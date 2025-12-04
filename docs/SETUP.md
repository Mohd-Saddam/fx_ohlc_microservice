# Setup Guide

This document provides detailed instructions for setting up the FX OHLC Microservice in both development and production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Docker Setup (Recommended)](#docker-setup-recommended)
- [Local Development Setup](#local-development-setup)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

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

## Installation Methods

Choose one of the following installation methods:

1. **Docker Setup** (Recommended) - Fastest and easiest, no Python setup required
2. **Local Development Setup** - For active development with hot reload

## Docker Setup (Recommended)

This is the simplest method that works consistently across all platforms.

### Step 1: Install Docker

#### Linux (Ubuntu/Debian)

```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

#### macOS

```bash
# Install Docker Desktop
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker compose version
```

#### Windows

1. Install Docker Desktop from https://www.docker.com/products/docker-desktop
2. Enable WSL2 integration
3. Restart your computer
4. Verify installation in PowerShell:
   ```powershell
   docker --version
   docker compose version
   ```

### Step 2: Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd fx_ohlc_microservice

# Verify you're in the correct directory
ls -la
# You should see: docker-compose.yml, Dockerfile, app/, tests/, etc.
```

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env  # or vim, code, etc.
```

Default `.env` configuration works out of the box. Modify only if needed:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fx_ohlc
REDIS_URL=redis://redis:6379/0
LOG_LEVEL=INFO
SYMBOL=EURUSD
DAY_START_HOUR=22
```

### Step 4: Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs to ensure everything started correctly
docker-compose logs -f

# Press Ctrl+C to stop viewing logs (services keep running)
```

### Step 5: Verify Installation

```bash
# Check that all containers are running
docker-compose ps

# You should see 3 services: api, db, redis - all "Up"

# Test the health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "redis": "connected",
#   ...
# }
```

### Step 6: Access the Application

Open your browser and visit:

- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **WebSocket Demo**: http://localhost:8000/demo

That's it! The application is now running with Docker.

## Local Development Setup

Use this setup for active development with features like hot reload, debugging, and direct code editing.

### Step 1: Install Python

#### Linux (Ubuntu/Debian)

```bash
# Install Python 3.10+
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3-pip

# Verify installation
python3 --version
```

#### macOS

```bash
# Install Python via Homebrew
brew install python@3.10

# Verify installation
python3 --version
```

#### Windows

1. Download Python 3.10+ from https://www.python.org/downloads/
2. Run installer (check "Add Python to PATH")
3. Verify in PowerShell:
   ```powershell
   python --version
   ```

### Step 2: Clone Repository

```bash
git clone <repository-url>
cd fx_ohlc_microservice
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

### Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
pip list
```

### Step 5: Start Infrastructure

The application needs PostgreSQL/TimescaleDB and Redis. Start them with Docker:

```bash
# Start only database and Redis (not the application)
docker-compose up -d db redis

# Verify they're running
docker-compose ps
```

### Step 6: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit for local development
nano .env
```

Update the `.env` file with local connection strings:

```env
# Use localhost instead of service names
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fx_ohlc
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=DEBUG
SYMBOL=EURUSD
DAY_START_HOUR=22
```

### Step 7: Run the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# The application will restart automatically when you edit code
```

### Step 8: Verify Installation

```bash
# In a new terminal, test the health endpoint
curl http://localhost:8000/health

# Access the API documentation
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux
start http://localhost:8000/docs  # Windows
```

## Database Setup

The database is automatically initialized when the application starts. However, you can manually verify or reinitialize if needed.

### Automatic Initialization

When the FastAPI application starts, it automatically:

1. Creates database tables
2. Converts `eurusd_ticks` to a TimescaleDB hypertable
3. Creates continuous aggregates (minute, hour, day)
4. Sets up refresh policies
5. Configures compression and retention

### Manual Database Inspection

```bash
# Connect to the database
docker-compose exec db psql -U postgres -d fx_ohlc

# Check tables
\dt

# Expected output:
#  public | eurusd_ticks | table | postgres

# Check hypertable
SELECT * FROM timescaledb_information.hypertables;

# Check continuous aggregates
SELECT view_name FROM timescaledb_information.continuous_aggregates;

# Expected output:
#  eurusd_ohlc_minute
#  eurusd_ohlc_hour
#  eurusd_ohlc_day

# Exit psql
\q
```

### Reset Database

If you need to start fresh:

```bash
# Stop all services
docker-compose down

# Remove database volume
docker-compose down -v

# Start services again (database will be recreated)
docker-compose up -d
```

## Configuration

### Environment Variables

All configuration is done through environment variables in the `.env` file.

#### Database Configuration

```env
# Connection string format:
# postgresql+asyncpg://user:password@host:port/database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fx_ohlc

# Connection pool settings
DB_POOL_SIZE=20          # Number of connections to keep open
DB_MAX_OVERFLOW=40       # Additional connections under load
```

#### Redis Configuration

```env
# Connection string format:
# redis://host:port/db_number
REDIS_URL=redis://redis:6379/0
```

#### Application Configuration

```env
# Logging
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Symbol to track
SYMBOL=EURUSD            # Can be any FX pair

# Custom day boundary (0-23 hours)
DAY_START_HOUR=22        # 22 = 10 PM UTC
```

#### TimescaleDB Configuration

```env
# Data management
COMPRESSION_AFTER_DAYS=7 # Days before compressing old data
RETENTION_DAYS=90        # Days to keep data before deletion
```

### Port Configuration

Default ports (modify in `docker-compose.yml` if needed):

- **API**: 8000
- **PostgreSQL**: 5432
- **Redis**: 6379

## Verification

### Health Check

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-12-05T10:30:00.000Z",
  "database": "connected",
  "redis": "connected",
  "version": "1.0.0"
}
```

### Data Flow Verification

```bash
# Wait 2-3 minutes for data to accumulate, then check tick count
docker-compose exec db psql -U postgres -d fx_ohlc -c "SELECT COUNT(*) FROM eurusd_ticks;"

# You should see a count > 0 and increasing

# Check OHLC aggregates
curl "http://localhost:8000/ohlc/minute?symbol=EURUSD&start=2025-12-05T10:00:00Z&end=2025-12-05T11:00:00Z"

# You should receive OHLC data
```

### WebSocket Verification

Open http://localhost:8000/demo in your browser. You should see:

- Live tick data updating every second
- OHLC data updating every few seconds
- Connection status showing "Connected"

## Troubleshooting

### Container Issues

**Problem**: Docker containers won't start

```bash
# Check Docker daemon is running
docker ps

# View detailed error logs
docker-compose logs api
docker-compose logs db

# Restart services
docker-compose restart
```

**Problem**: Port already in use

```bash
# Find process using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
```

### Database Issues

**Problem**: Cannot connect to database

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify database is accepting connections
docker-compose exec db pg_isready -U postgres
```

**Problem**: Tables not created

```bash
# Check application logs
docker-compose logs api | grep -i "table\|hypertable"

# Manually reinitialize (if needed)
docker-compose restart api
```

### Application Issues

**Problem**: Application returns 500 errors

```bash
# Check application logs
docker-compose logs api --tail=100

# Common causes:
# 1. Database not ready (wait 10-20 seconds)
# 2. Environment variables misconfigured (check .env)
# 3. Dependency issues (rebuild: docker-compose up --build)
```

**Problem**: No tick data appearing

```bash
# Check tick generator is running
docker-compose logs api | grep "Publishing tick"

# Should see: "Publishing tick: ..." every second

# If not, check Redis connection
docker-compose logs redis
```

### Permission Issues (Linux)

```bash
# If you get permission denied errors
sudo usermod -aG docker $USER

# Log out and log back in, then verify
docker ps
```

### Python Virtual Environment Issues

**Problem**: Cannot activate virtual environment

```bash
# Make sure you created it first
python3 -m venv venv

# On Windows, you might need to allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Problem**: Module not found errors

```bash
# Ensure virtual environment is activated (you should see (venv) in prompt)
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Getting Help

If you encounter issues not covered here:

1. Check the logs: `docker-compose logs -f`
2. Verify your `.env` file configuration
3. Ensure all prerequisites are installed
4. Try a fresh start: `docker-compose down -v && docker-compose up -d`
5. Check GitHub issues (if applicable)

---

**Next Steps**: After successful setup, see [README.md](README.md) for API usage and [TESTING.md](TESTING.md) for running tests.
