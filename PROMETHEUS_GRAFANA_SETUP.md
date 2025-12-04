# Prometheus & Grafana Monitoring - Complete Setup

## What Was Added

### 1. Docker Services

Added 4 new monitoring services to `docker-compose.yml`:

- **prometheus**: Metrics collection and storage (port 9090)
- **grafana**: Visualization dashboards (port 3000)
- **postgres-exporter**: PostgreSQL/TimescaleDB metrics (port 9187)
- **redis-exporter**: Redis metrics (port 9121)

### 2. Configuration Files

- `prometheus.yml`: Prometheus scrape configuration
- `grafana-datasource.yml`: Auto-configured Prometheus data source
- `grafana-dashboards.yml`: Dashboard provisioning
- `grafana-dashboard.json`: Pre-built FX OHLC dashboard

### 3. Application Metrics

Added `app/metrics.py` with custom Prometheus metrics:

**Tick Ingestion**:
- `ticks_ingested_total`: Total ticks ingested
- `ticks_ingestion_duration_seconds`: Ingestion latency
- `bulk_ticks_ingested_total`: Bulk ingestion counter

**OHLC Queries**:
- `ohlc_queries_total`: Total OHLC queries
- `ohlc_query_duration_seconds`: Query latency histogram
- `ohlc_rows_returned`: Rows returned histogram

**WebSocket**:
- `websocket_connections_active`: Active connections gauge
- `websocket_messages_sent_total`: Messages sent counter
- `websocket_errors_total`: WebSocket errors

**Database**:
- `db_query_duration_seconds`: Database query latency
- `db_connection_pool_size`: Connection pool metrics
- `pg_stat_database_numbackends`: Active connections (from exporter)

**Redis**:
- `redis_messages_published_total`: Published messages
- `redis_messages_received_total`: Received messages
- `redis_connected_clients`: Active clients (from exporter)

### 4. Auto-Instrumentation

Updated `requirements.txt` with:
- `prometheus-client==0.20.0`
- `prometheus-fastapi-instrumentator==7.0.0`

Updated `app/main.py` with:
- Prometheus FastAPI auto-instrumentation
- `/metrics` endpoint for Prometheus scraping
- Automatic HTTP metrics collection

## Quick Start

```bash
# Start all services including monitoring
docker-compose up -d

# Verify services
docker-compose ps | grep -E "prometheus|grafana|exporter"

# Access Grafana
open http://localhost:3000  # admin/admin

# Access Prometheus
open http://localhost:9090

# View metrics
curl http://localhost:8000/metrics
```

## Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| Grafana | 3000 | Dashboards and visualization |
| Prometheus | 9090 | Metrics storage and query |
| Postgres Exporter | 9187 | PostgreSQL metrics |
| Redis Exporter | 9121 | Redis metrics |
| API /metrics | 8000 | Application metrics endpoint |

## Pre-configured Dashboard

The **FX OHLC Microservice Dashboard** includes:

1. **Request Rate**: Real-time HTTP requests/sec
2. **Request Latency (P95)**: 95th percentile latency
3. **Database Connections**: Active PostgreSQL connections
4. **Redis Connections**: Active Redis clients
5. **Tick Ingestion Rate**: Ticks processed/sec

## Example Queries

### Application Performance

```promql
# Request rate by endpoint
rate(http_requests_total[1m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[1m])
```

### Data Pipeline

```promql
# Tick ingestion rate
rate(ticks_ingested_total{symbol="EURUSD"}[1m])

# OHLC query performance
histogram_quantile(0.95, rate(ohlc_query_duration_seconds_bucket[5m]))

# WebSocket connections
websocket_connections_active
```

### Infrastructure

```promql
# Database connections
pg_stat_database_numbackends{datname="fxohlc"}

# Redis memory
redis_memory_used_bytes

# Database cache hit ratio
pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)
```

## Alerting (Optional)

Create `prometheus-alerts.yml`:

```yaml
groups:
  - name: fx_ohlc_alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency"

      - alert: TickIngestionStopped
        expr: rate(ticks_ingested_total[5m]) == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Tick ingestion stopped"
```

## Production Considerations

1. **Retention**: Configure Prometheus retention based on storage
   ```yaml
   prometheus:
     command:
       - '--storage.tsdb.retention.time=30d'
       - '--storage.tsdb.retention.size=10GB'
   ```

2. **Security**: Change default Grafana password
   ```yaml
   grafana:
     environment:
       - GF_SECURITY_ADMIN_PASSWORD=your-secure-password
   ```

3. **Persistence**: Data is stored in Docker volumes
   - `prometheus_data`
   - `grafana_data`

4. **Scaling**: For production, consider:
   - External Prometheus (e.g., Grafana Cloud, Datadog)
   - Multiple Prometheus instances with federation
   - Long-term storage with Thanos or Cortex

## Troubleshooting

### Metrics not appearing

```bash
# Check API metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Prometheus logs
docker-compose logs prometheus
```

### Grafana dashboard empty

1. Verify Prometheus data source connection
2. Check time range (last 1 hour)
3. Ensure services are running and generating metrics

### Exporter connection issues

```bash
# Check exporter logs
docker-compose logs postgres-exporter
docker-compose logs redis-exporter

# Verify connectivity
docker-compose exec prometheus wget -O- postgres-exporter:9187/metrics
```

## Documentation

- **Detailed Guide**: [docs/MONITORING.md](docs/MONITORING.md)
- **Quick Start**: [MONITORING_QUICKSTART.md](MONITORING_QUICKSTART.md)
- **Main README**: [README.md](README.md#monitoring)

## Benefits

1. **Visibility**: Real-time insight into application performance
2. **Alerting**: Proactive issue detection
3. **Debugging**: Historical metrics for troubleshooting
4. **Capacity Planning**: Data-driven scaling decisions
5. **SLA Monitoring**: Track latency and availability

## Next Steps

1. Customize dashboards for your needs
2. Set up alerting rules
3. Configure notification channels (Slack, PagerDuty, etc.)
4. Export metrics to external monitoring services
5. Create custom panels for business metrics

---

**All monitoring services are production-ready and start automatically with `docker-compose up -d`**
