# Quick Reference - Files Modified & Commands

## 📁 Files Modified

### 1. **docker-compose.yml** ⭐ MAIN FILE
```
Location: /Users/anandprakashmishra/Desktop/Danger/mac-automation-app/docker-compose.yml

Changes:
✓ Line 8:   ports: "8080:5000" (was 5000:5000)
✓ Line 32:  ports: "19090:9090" (was 9090:9090)
✓ Lines 20-24:   Added logging config to web-app
✓ Lines 37-41:   Added logging config to prometheus
✓ Lines 48-52:   Added logging config to grafana
✓ Lines 59-63:   Added logging config to loki
✓ Lines 70-74:   Added logging config to promtail
✓ Lines 100-180: Added inline configs section (prometheus, loki, promtail)
```

### 2. **.env**
```
Location: /Users/anandprakashmishra/Desktop/Danger/mac-automation-app/.env

Content:
HOST_USER=anandprakashmishra
HOST_PASSWORD=your_password
```

### 3. **.env.example**
```
Location: /Users/anandprakashmishra/Desktop/Danger/mac-automation-app/.env.example

Content:
HOST_USER=your_mac_username
HOST_PASSWORD=your_mac_password
```

---

## 🚀 Commands to Run (In Order)

### Step 1: Update .env
```bash
cd /Users/anandprakashmishra/Desktop/Danger/mac-automation-app
nano .env
# Add your credentials:
# HOST_USER=anandprakashmishra
# HOST_PASSWORD=your_actual_password
```

### Step 2: Restart Docker
```bash
docker-compose down
docker-compose up -d
```

### Step 3: Verify
```bash
docker ps
curl http://localhost:8080
curl http://localhost:19090/-/healthy
```

---

## 🎯 What Each Change Does

| Change | Purpose | Result |
|--------|---------|--------|
| Port 8080 | Avoid macOS ControlCenter conflict | App accessible at :8080 |
| Port 19090 | Avoid Electron process conflict | Prometheus at :19090 |
| Inline configs | Fix Docker Desktop permissions | No file sharing needed |
| Logging config | 50MB log limit | Auto-rotate logs |
| Loki retention | 7-day limit | Auto-delete old logs |

---

## 📊 Service URLs

After running commands:

- **Main App**: http://localhost:8080
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:19090
- **Loki**: http://localhost:3100

---

## 🔧 Key Configuration Snippets

### Logging (Add to each service)
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "50m"
    max-file: "3"
```

### Prometheus Config (Inline)
```yaml
configs:
  prometheus_config:
    content: |
      global:
        scrape_interval: 15s
      scrape_configs:
        - job_name: 'mac_automation_app'
          static_configs:
            - targets: ['web-app:5000']
```

### Loki Retention
```yaml
limits_config:
  retention_period: 168h  # 7 days
  ingestion_rate_mb: 50
```

---

## ✅ Verification Commands

```bash
# All containers running?
docker ps

# Logging configured?
docker inspect mac-automation-app | grep -A 5 LogConfig

# Services healthy?
curl http://localhost:8080
curl http://localhost:19090/-/healthy
curl http://localhost:3000/api/health

# Loki working?
docker logs loki | grep "Loki started"
```

---

## 📚 Full Documentation

For detailed explanations, see:
- `SETUP_GUIDE.md` - Complete step-by-step guide
- `LOG_MANAGEMENT.md` - Log rotation details
- `PROMETHEUS_FIX.md` - Prometheus fix explanation
- `GRAFANA_GUIDE.md` - Grafana setup
- `PORT_FIX.md` - Port conflict resolution
