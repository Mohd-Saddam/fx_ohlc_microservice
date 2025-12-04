# 📚 FX OHLC Microservice - Documentation

This directory contains all project documentation and assets.

## 📖 Documentation Files

### [SETUP.md](SETUP.md)
Complete installation and configuration guide:
- Prerequisites (Docker, Python, etc.)
- Docker setup instructions
- Local development setup
- Database initialization
- Configuration options
- Troubleshooting guide

### [TESTING.md](TESTING.md)
Comprehensive testing documentation:
- Test structure and organization
- Running tests (unit, integration, coverage)
- Writing new tests
- Test fixtures and configurations
- CI/CD integration
- Best practices

### [architecture-diagram.md](architecture-diagram.md)
High-level system architecture diagram:
- Visual representation of the entire system
- Client applications layer
- FastAPI microservice layers (API, Business Logic, Background Services)
- Data storage (Redis Pub/Sub, TimescaleDB)
- Data flow explanation

## 🖼️ Screenshots & Assets

### websocket-demo.png
Screenshot of the WebSocket live demo page showing:
- Real-time tick data streaming
- OHLC endpoint selection buttons (Minute, Hourly, Daily)
- Live statistics (avg, min, max prices)
- Message log with real-time updates
- Connection controls (Connect, Disconnect, Clear)

**To add the screenshot:**
1. Open `http://localhost:8000/ws-test` in your browser
2. Take a screenshot of the page
3. Save it as `websocket-demo.png` in this directory
4. The main README will automatically display it

**Current Status:** ⚠️ Screenshot needs to be added manually

**Expected Location:**
```
/Users/saddam/Documents/fast_api/fx_ohlc_microservice/docs/websocket-demo.png
```

---

## 📂 Directory Structure

```
docs/
├── README.md                # This file - documentation index
├── SETUP.md                 # Installation and setup guide
├── TESTING.md               # Testing documentation
├── architecture-diagram.md  # High-level system architecture
└── websocket-demo.png       # Screenshot (to be added)
```

---

**Note:** All documentation is organized in this folder to keep the project root clean. The main README.md in the project root provides an overview and links to these detailed guides.
