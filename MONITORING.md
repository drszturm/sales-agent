# Grafana Monitoring Setup for Sales Agent

This setup includes Prometheus metrics collection and Grafana dashboards to visualize function performance across your sales-agent application.

## Architecture

- **Prometheus**: Scrapes metrics from the FastAPI `/metrics` endpoint every 15 seconds
- **Grafana**: Visualizes Prometheus data with pre-built dashboards
- **FastAPI**: Exposes metrics via `prometheus_client` library at `http://localhost:8000/metrics`

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all services (app + redis + prometheus + grafana)
docker-compose up -d

# View logs
docker-compose logs -f app
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### Access the UIs

- **Grafana Dashboard**: http://localhost:3000
  - Default credentials: `admin` / `admin` (or set via `GRAFANA_PASSWORD` env var)
  - Dashboard: **Sales Agent - Function Metrics**

- **Prometheus**: http://localhost:9090
  - Query metrics manually: http://localhost:9090/graph
  - Example query: `function_calls_total` or `avg by (function) (rate(function_duration_seconds[5m]))`

- **Application Metrics (raw)**: http://localhost:8000/metrics

## Grafana Panels Included

### 1. **Function Calls (5m rate)**
   - Time series showing call rate per function over 5-minute windows
   - Helps identify traffic spikes and usage patterns

### 2. **Average Function Duration (5m)**
   - Tracks mean execution time for each instrumented function
   - Color-coded alerts if duration exceeds 5 seconds

### 3. **Function Duration Percentiles (5m)**
   - P95 and P99 percentiles for latency analysis
   - Useful for understanding tail-end performance issues

### 4. **Call Rate per Function (1m)**
   - Current requests-per-second for each function
   - Visual stat panel with color thresholds

### 5. **Total Function Calls**
   - Cumulative total calls across all time
   - Helps track total workload

### 6. **Max Function Duration (5m)**
   - Peak execution time observed in the last 5 minutes
   - Quick visual alert for performance degradation

## Configuration

### Environment Variables

Set these in your `.env` file or pass to `docker-compose`:

```bash
GRAFANA_USER=admin          # Grafana admin username (default: admin)
GRAFANA_PASSWORD=mypasswd   # Grafana admin password (default: admin)
```

### Prometheus Configuration

Edit `prometheus.yml` to customize:
- Scrape interval (currently 15s)
- Evaluation interval (currently 15s)
- Add more `scrape_configs` for additional services

Example: Add another application:
```yaml
  - job_name: 'other-service'
    static_configs:
      - targets: ['other-service:9000']
    metrics_path: '/metrics'
```

### Grafana Dashboard

The dashboard is automatically provisioned via `grafana/provisioning/dashboards/dashboards.yml`. 

To manually import or edit:
1. Visit http://localhost:3000/dashboards
2. Find "Sales Agent - Function Metrics"
3. Click to view or edit

## Metrics Available

Your application exposes these Prometheus metrics (via `shared/metrics.py`):

- `function_calls_total` (Counter): Total function invocations by function name
- `function_duration_seconds` (Histogram): Execution time distribution with buckets for P50, P95, P99, etc.

All metrics are labeled by `function` name for easy filtering and grouping.

## Example PromQL Queries

Paste these into Prometheus (http://localhost:9090/graph) to explore:

```promql
# Call rate per function (1 minute)
rate(function_calls_total[1m])

# Average latency per function (5 minutes)
avg by (function) (rate(function_duration_seconds_sum[5m]) / rate(function_duration_seconds_count[5m]))

# P95 latency percentile
histogram_quantile(0.95, rate(function_duration_seconds_bucket[5m]))

# Functions with most calls
topk(5, rate(function_calls_total[5m]))

# Slowest functions (by average)
topk(5, avg by (function) (rate(function_duration_seconds_sum[5m]) / rate(function_duration_seconds_count[5m])))
```

## Stopping Services

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (careful: loses Grafana/Prometheus data)
docker-compose down -v
```

## Persistence

Data is stored in Docker volumes:
- `prometheus_data`: Prometheus time-series database
- `grafana_data`: Grafana settings and dashboards
- `redis_data`: Redis persistence

Volumes persist across container restarts unless explicitly deleted.

## Troubleshooting

### Prometheus not scraping metrics

1. Check app is running: `curl http://localhost:8000/health`
2. Check metrics endpoint: `curl http://localhost:8000/metrics`
3. View Prometheus targets: http://localhost:9090/targets
4. Check Prometheus logs: `docker-compose logs prometheus`

### Grafana can't reach Prometheus

1. Ensure Prometheus is running: `docker-compose ps`
2. Check datasource config: **Configuration** → **Data Sources** → **Prometheus**
3. Test connection by clicking "Save & Test"
4. Verify network: `docker network inspect sales-network`

### Dashboard showing no data

1. Wait 30+ seconds for initial scrape
2. Check Prometheus for data: http://localhost:9090/graph
3. Verify functions are being instrumented (@instrument decorator present)
4. Query a simple metric: `function_calls_total` or `up{job="sales-agent"}`

## Advanced: Custom Panels

To add new panels to the dashboard:

1. Visit http://localhost:3000
2. Open **Sales Agent - Function Metrics** dashboard
3. Click **Add panel** → **Add a new panel**
4. Choose visualization (time series, stat, gauge, etc.)
5. Write PromQL query from examples above
6. Click **Save**

Dashboard changes are auto-saved to the JSON file and persisted in Grafana's database.

## Next Steps

- **Set up alerts** in Grafana to notify on performance thresholds
- **Expand metrics** by instrumenting additional functions
- **Integrate with PagerDuty/Slack** for alerting
- **Export/backup** dashboards via Grafana UI or API
- **Scale monitoring** by adding more scrape targets

## References

- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Docs](https://grafana.com/docs/)
- [prometheus_client Python](https://github.com/prometheus/client_python)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
