# Prometheus & Grafana Quick Start

## Start Monitoring Stack

```bash
# Start all services (includes Prometheus & Grafana)
docker-compose up -d

# Verify services are running
docker-compose ps
```

## Access Dashboards

1. **Grafana**: http://localhost:3000
   - Username: `admin`
   - Password: `admin`
   - Dashboard: **FX OHLC Microservice Dashboard**

2. **Prometheus**: http://localhost:9090
   - Check targets: http://localhost:9090/targets

3. **API Metrics**: http://localhost:8000/metrics

## Key Metrics to Watch

### Application Health
- Request Rate: `rate(http_requests_total[1m])`
- Latency (P95): `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- Error Rate: `rate(http_requests_total{status=~"5.."}[1m])`

### Data Pipeline
- Tick Ingestion Rate: `rate(ticks_ingested_total[1m])`
- OHLC Query Rate: `rate(ohlc_queries_total[1m])`
- WebSocket Connections: `websocket_connections_active`

### Infrastructure
- Database Connections: `pg_stat_database_numbackends{datname="fxohlc"}`
- Redis Clients: `redis_connected_clients`
- Memory Usage: `redis_memory_used_bytes`

## Troubleshooting

**Metrics not showing?**
```bash
# Check if Prometheus can scrape FastAPI
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq
```

**Grafana dashboard empty?**
1. Go to Configuration → Data Sources
2. Test the Prometheus connection
3. Reimport the dashboard from JSON

## Next Steps

- Set up alerts in Prometheus
- Create custom dashboards in Grafana
- Export metrics to external monitoring services
- Configure retention policies

See [docs/MONITORING.md](docs/MONITORING.md) for detailed documentation.
