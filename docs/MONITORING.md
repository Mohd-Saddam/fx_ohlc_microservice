# Monitoring Setup Guide

This guide covers Prometheus and Grafana monitoring setup for the FX OHLC Microservice.

## Overview

The monitoring stack includes:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Postgres Exporter**: PostgreSQL/TimescaleDB metrics
- **Redis Exporter**: Redis metrics
- **Custom Metrics**: Application-specific metrics

## Quick Start

All monitoring components are included in the Docker Compose setup:

```bash
# Start all services including monitoring
docker-compose up -d

# Verify monitoring services
docker-compose ps | grep -E "prometheus|grafana|exporter"
```

## Access URLs

Once running, access the monitoring interfaces:

- **Grafana Dashboard**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`
  
- **Prometheus UI**: http://localhost:9090

- **API Metrics Endpoint**: http://localhost:8000/metrics

## Grafana Dashboard

### Default Dashboard

The pre-configured dashboard includes:

1. **Request Rate**: HTTP requests per second by endpoint
2. **Request Latency**: P95 latency for all endpoints
3. **Database Connections**: Active PostgreSQL connections
4. **Redis Connections**: Active Redis clients
5. **Tick Ingestion Rate**: Ticks processed per second

### Accessing the Dashboard

1. Open http://localhost:3000
2. Login with `admin`/`admin`
3. Navigate to **Dashboards** → **FX OHLC Microservice Dashboard**

### Creating Custom Dashboards

1. Click **+** → **Dashboard**
2. Add Panel
3. Select **Prometheus** as data source
4. Enter PromQL query (see examples below)

## Available Metrics

### Application Metrics

**Tick Ingestion**:
```promql
# Tick ingestion rate
rate(ticks_ingested_total[1m])

# Total ticks ingested
ticks_ingested_total{symbol="EURUSD"}

# Ingestion duration
histogram_quantile(0.95, rate(ticks_ingestion_duration_seconds_bucket[5m]))
```

**OHLC Queries**:
```promql
# OHLC query rate
rate(ohlc_queries_total[1m])

# OHLC query duration (p95)
histogram_quantile(0.95, rate(ohlc_query_duration_seconds_bucket[5m]))

# OHLC rows returned
histogram_quantile(0.95, rate(ohlc_rows_returned_bucket[5m]))
```

**WebSocket Connections**:
```promql
# Active WebSocket connections
websocket_connections_active

# WebSocket messages sent
rate(websocket_messages_sent_total[1m])

# WebSocket errors
rate(websocket_errors_total[1m])
```

### HTTP Metrics (Auto-instrumented)

```promql
# Request rate by endpoint
rate(http_requests_total[1m])

# Request duration (p50, p95, p99)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Requests in progress
http_requests_in_progress

# Request size
histogram_quantile(0.95, rate(http_request_size_bytes_bucket[5m]))
```

### Database Metrics

**PostgreSQL**:
```promql
# Active connections
pg_stat_database_numbackends{datname="fxohlc"}

# Transactions per second
rate(pg_stat_database_xact_commit{datname="fxohlc"}[1m])

# Cache hit ratio
pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)

# Table size
pg_stat_user_tables_n_live_tup{relname="eurusd_ticks"}
```

**TimescaleDB**:
```promql
# Hypertable chunks
hypertable_chunks_total{hypertable="eurusd_ticks"}

# Compressed chunks
compressed_chunks_total{hypertable="eurusd_ticks"}

# Continuous aggregate refresh duration
continuous_aggregate_refresh_duration_seconds
```

### Redis Metrics

```promql
# Connected clients
redis_connected_clients

# Commands per second
rate(redis_commands_processed_total[1m])

# Memory usage
redis_memory_used_bytes

# Keyspace hits ratio
redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)
```

## Alerting

### Configure Alert Rules

Create `prometheus-alerts.yml`:

```yaml
groups:
  - name: fx_ohlc_alerts
    interval: 30s
    rules:
      - alert: HighRequestLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency detected"
          description: "P95 latency is above 1 second"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "More than 5% of requests are failing"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends{datname="fxohlc"} > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database has more than 80 active connections"

      - alert: TickIngestionStopped
        expr: rate(ticks_ingested_total[5m]) == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Tick ingestion has stopped"
          description: "No ticks ingested in the last 2 minutes"
```

Update `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - 'prometheus-alerts.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  # ... existing configs
```

## Performance Tuning

### Prometheus Retention

Adjust retention in `docker-compose.yml`:

```yaml
prometheus:
  command:
    - '--storage.tsdb.retention.time=30d'
    - '--storage.tsdb.retention.size=10GB'
```

### Scrape Interval

For high-frequency updates, adjust scrape intervals in `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'fastapi'
    scrape_interval: 5s  # Faster for real-time metrics
```

## Troubleshooting

### Prometheus Not Scraping Metrics

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check API metrics endpoint
curl http://localhost:8000/metrics
```

### Grafana Dashboard Not Loading

```bash
# Check Grafana logs
docker-compose logs grafana

# Verify data source connection
# Go to Configuration → Data Sources in Grafana UI
```

### High Memory Usage

```bash
# Check Prometheus storage
du -sh prometheus_data/

# Reduce retention or increase storage limit
```

## Monitoring Best Practices

1. **Set Up Alerts**: Configure alerts for critical metrics
2. **Dashboard Organization**: Group related metrics together
3. **Use Labels**: Add labels to metrics for better filtering
4. **Regular Review**: Review dashboards weekly to identify trends
5. **Capacity Planning**: Monitor growth trends for scaling decisions

## Integration with External Services

### Grafana Cloud

Export dashboard JSON and import to Grafana Cloud:

```bash
# Export dashboard
curl http://localhost:3000/api/dashboards/uid/fx-ohlc-dashboard \
  -u admin:admin > dashboard-export.json
```

### Datadog/New Relic

Add remote write configuration to `prometheus.yml`:

```yaml
remote_write:
  - url: "https://your-datadog-endpoint/api/v1/series"
    basic_auth:
      username: "your-api-key"
```

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter)
- [Redis Exporter](https://github.com/oliver006/redis_exporter)
