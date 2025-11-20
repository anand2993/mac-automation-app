# Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Docker Host (Mac)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Docker Network: monitoring                     │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │   Web App    │  │  Prometheus  │  │   Grafana    │    │ │
│  │  │              │  │              │  │              │    │ │
│  │  │ Port: 8080   │  │ Port: 19090  │  │ Port: 3000   │    │ │
│  │  │              │  │              │  │              │    │ │
│  │  │ Logs: 50MB   │  │ Logs: 50MB   │  │ Logs: 50MB   │    │ │
│  │  │ Files: 3     │  │ Files: 3     │  │ Files: 3     │    │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │ │
│  │         │                 │                 │             │ │
│  │         │                 │                 │             │ │
│  │  ┌──────▼───────┐  ┌──────▼───────┐                      │ │
│  │  │     Loki     │  │   Promtail   │                      │ │
│  │  │              │  │              │                      │ │
│  │  │ Port: 3100   │  │  (internal)  │                      │ │
│  │  │              │  │              │                      │ │
│  │  │ Retention:   │  │ Logs: 50MB   │                      │ │
│  │  │ 7 days       │  │ Files: 3     │                      │ │
│  │  │ Logs: 50MB   │  │              │                      │ │
│  │  └──────────────┘  └──────────────┘                      │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Configuration Files                      │ │
│  │                  (Inline in docker-compose.yml)             │ │
│  │                                                             │ │
│  │  • prometheus_config  (scrape metrics)                     │ │
│  │  • loki_config        (log storage, retention)             │ │
│  │  • promtail_config    (log collection)                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. **Application Metrics Flow**
```
Web App (Flask)
    │
    ├─► Exposes /metrics endpoint
    │
    ▼
Prometheus
    │
    ├─► Scrapes metrics every 15s
    │
    ▼
Grafana
    │
    └─► Visualizes metrics in dashboards
```

### 2. **Log Collection Flow**
```
All Docker Containers
    │
    ├─► Write logs to stdout/stderr
    │
    ▼
Docker JSON Log Driver
    │
    ├─► Rotates at 50MB (keeps 3 files)
    │
    ▼
Promtail
    │
    ├─► Collects logs from Docker
    │
    ▼
Loki
    │
    ├─► Stores logs (7-day retention)
    │
    ▼
Grafana
    │
    └─► Query and view logs
```

### 3. **User Access Flow**
```
User Browser
    │
    ├─► http://localhost:8080    → Web App
    ├─► http://localhost:3000    → Grafana
    └─► http://localhost:19090   → Prometheus
```

---

## 📦 Container Details

### Web App
- **Image**: Custom (built from Dockerfile)
- **Port**: 8080 → 5000 (internal)
- **Purpose**: Mac automation web interface
- **Metrics**: Exposed at `/metrics`
- **Logs**: 50MB × 3 files

### Prometheus
- **Image**: prom/prometheus:latest
- **Port**: 19090 → 9090 (internal)
- **Purpose**: Metrics collection and storage
- **Scrapes**: Web app every 15 seconds
- **Logs**: 50MB × 3 files

### Grafana
- **Image**: grafana/grafana:latest
- **Port**: 3000
- **Purpose**: Visualization and dashboards
- **Data Sources**: Prometheus, Loki
- **Logs**: 50MB × 3 files

### Loki
- **Image**: grafana/loki:latest
- **Port**: 3100
- **Purpose**: Log aggregation and storage
- **Retention**: 7 days (168 hours)
- **Logs**: 50MB × 3 files

### Promtail
- **Image**: grafana/promtail:latest
- **Port**: None (internal)
- **Purpose**: Log collection from Docker
- **Sends to**: Loki at http://loki:3100
- **Logs**: 50MB × 3 files

---

## 🔧 Configuration Strategy

### Why Inline Configs?

**Problem**: Docker Desktop on Mac doesn't have permission to access Desktop folder

**Solution**: Embed configs directly in docker-compose.yml

```yaml
# ❌ Old way (doesn't work on Desktop)
volumes:
  - ./prometheus.yml:/etc/prometheus/prometheus.yml

# ✅ New way (works everywhere)
configs:
  - source: prometheus_config
    target: /etc/prometheus/prometheus.yml

configs:
  prometheus_config:
    content: |
      # Config content here
```

**Benefits**:
- ✅ No file permission issues
- ✅ Works from any directory
- ✅ All config in one place
- ✅ Easy to version control

---

## 📊 Log Management Strategy

### Docker Container Logs

```
Each Container:
  ├─► Current log file (growing)
  ├─► Rotated file 1 (50MB)
  └─► Rotated file 2 (50MB)

When current reaches 50MB:
  ├─► Rotate: current → file 1
  ├─► Rotate: file 1 → file 2
  └─► Delete: file 2 (oldest)

Total per container: ~150MB max
```

### Loki Log Retention

```
Loki Storage:
  ├─► Incoming logs (unlimited rate: 50MB/s)
  ├─► Store for 7 days
  └─► Compactor runs every 2 hours
      └─► Deletes logs older than 7 days

Result: Automatic cleanup, no manual intervention
```

---

## 🎯 Port Mapping

| Service | Host Port | Container Port | Why This Port? |
|---------|-----------|----------------|----------------|
| Web App | 8080 | 5000 | Avoid macOS ControlCenter (uses 5000) |
| Prometheus | 19090 | 9090 | Avoid Electron process (uses 9090) |
| Grafana | 3000 | 3000 | No conflict |
| Loki | 3100 | 3100 | No conflict |
| Promtail | - | - | Internal only |

---

## 🔐 Security & Credentials

### Environment Variables (.env)
```
HOST_USER=anandprakashmishra
HOST_PASSWORD=your_mac_password
```

### Service Credentials
- **Web App**: admin / password123
- **Grafana**: admin / admin (change on first login)
- **Prometheus**: No authentication
- **Loki**: No authentication

---

## 📈 Monitoring Metrics

### Available Metrics

```python
# Request counter
app_request_count{method="GET", endpoint="/"}

# App open counter
app_open_count{app_name="facetime"}

# System status
system_status  # 1 = Up, 0 = Down
```

### Prometheus Queries

```promql
# Total requests
sum(app_request_count)

# Request rate (per minute)
rate(app_request_count[1m]) * 60

# Most opened apps
topk(5, app_open_count)
```

---

## 🛠️ Maintenance

### Daily Operations

```bash
# Check status
docker ps

# View logs
docker logs -f mac-automation-app

# Restart service
docker-compose restart web-app
```

### Weekly Maintenance

```bash
# Check log sizes
docker ps --format "table {{.Names}}\t{{.Size}}"

# Check disk usage
docker system df
```

### Monthly Cleanup

```bash
# Clean up unused resources
docker system prune

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

---

## 🚀 Scaling Considerations

### Current Setup
- Single instance of each service
- Suitable for development/testing
- Low resource usage

### Production Recommendations
1. **Add authentication** to Prometheus/Loki
2. **Use external volumes** for data persistence
3. **Set up backups** for Grafana dashboards
4. **Increase retention** if needed
5. **Add alerting** via Grafana/Prometheus

---

## 📚 File Structure

```
mac-automation-app/
├── app/
│   └── main.py                    # Flask application
├── docker-compose.yml             # Main configuration ⭐
├── Dockerfile                     # App container build
├── .env                          # Credentials (gitignored)
├── .env.example                  # Template
├── .gitignore                    # Git ignore rules
├── azure-pipelines.yml           # CI/CD pipeline
├── requirements.txt              # Python dependencies
│
├── Documentation/
│   ├── SETUP_GUIDE.md           # Complete setup guide ⭐
│   ├── QUICK_REFERENCE.md       # Quick commands
│   ├── LOG_MANAGEMENT.md        # Log rotation guide
│   ├── PROMETHEUS_FIX.md        # Prometheus fix
│   ├── GRAFANA_GUIDE.md         # Grafana usage
│   ├── PORT_FIX.md              # Port conflicts
│   └── grafana-dashboard.json   # Dashboard template
│
└── (Old config files - no longer used)
    ├── prometheus.yml
    ├── loki-config.yml
    └── promtail-config.yml
```

---

## ✅ Success Criteria

Your setup is working correctly if:

- [ ] All 5 containers running (`docker ps`)
- [ ] Web app accessible at http://localhost:8080
- [ ] Grafana accessible at http://localhost:3000
- [ ] Prometheus accessible at http://localhost:19090
- [ ] Metrics visible in Prometheus
- [ ] Logs visible in Grafana (via Loki)
- [ ] Log rotation configured (check with `docker inspect`)
- [ ] No port conflicts
- [ ] Loki compactor running

---

## 🎉 Summary

This architecture provides:
- ✅ **Monitoring**: Prometheus + Grafana
- ✅ **Logging**: Loki + Promtail
- ✅ **Log Management**: Auto-rotation (50MB limit)
- ✅ **Retention**: 7-day automatic cleanup
- ✅ **No Permission Issues**: Inline configs
- ✅ **No Port Conflicts**: Custom ports
- ✅ **Easy Maintenance**: Single docker-compose.yml

**Everything runs automatically with zero manual intervention!** 🚀
