# Complete Setup Guide - Step by Step

This guide shows you exactly what was done and how to reproduce it from scratch.

---

## 📋 Overview

Here's what was configured:
1. ✅ Fixed port conflicts (5000 → 8080, 9090 → 19090)
2. ✅ Fixed Prometheus/Loki Docker permissions issue
3. ✅ Configured 50MB log limits with auto-rotation
4. ✅ Set up 7-day log retention in Loki
5. ✅ Created monitoring dashboards

---

## 📁 Files Modified

### 1. **docker-compose.yml** (Main Configuration)
**Location**: `/Users/anandprakashmishra/Desktop/Danger/mac-automation-app/docker-compose.yml`

**Changes Made**:
- Changed web-app port from `5000:5000` to `8080:5000`
- Changed Prometheus port from `9090:9090` to `19090:9090`
- Converted all config files (prometheus.yml, loki-config.yml, promtail-config.yml) to inline configs
- Added logging configuration to all services (50MB limit, 3 files)
- Added Loki retention and compactor settings

### 2. **.env** (Environment Variables)
**Location**: `/Users/anandprakashmishra/Desktop/Danger/mac-automation-app/.env`

**Changes Made**:
- Simplified to only include `HOST_USER` and `HOST_PASSWORD`

### 3. **.env.example** (Template)
**Location**: `/Users/anandprakashmishra/Desktop/Danger/mac-automation-app/.env.example`

**Changes Made**:
- Simplified to match `.env` structure

### 4. **Documentation Files Created**:
- `PORT_FIX.md` - Port conflict resolution guide
- `PROMETHEUS_FIX.md` - Prometheus Docker fix documentation
- `GRAFANA_GUIDE.md` - How to use Grafana
- `LOG_MANAGEMENT.md` - Log rotation and retention guide
- `grafana-dashboard.json` - Pre-built Grafana dashboard

---

## 🚀 Step-by-Step Reproduction Guide

### **Step 1: Update .env File**

Create/update `.env` with your Mac credentials:

```bash
cd /Users/anandprakashmishra/Desktop/Danger/mac-automation-app

cat > .env << 'EOF'
# Mac Host Credentials
HOST_USER=anandprakashmishra
HOST_PASSWORD=your_actual_mac_password
EOF
```

**Important**: Replace `your_actual_mac_password` with your real Mac password.

---

### **Step 2: Update docker-compose.yml**

The main changes to `docker-compose.yml`:

#### **A. Change Ports** (Lines 7-8, 32)

```yaml
# Web app port (was 5000:5000)
ports:
  - "8080:5000"

# Prometheus port (was 9090:9090)
ports:
  - "19090:9090"
```

#### **B. Add Logging to Each Service**

Add this to **every service** (web-app, prometheus, grafana, loki, promtail):

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "50m"
    max-file: "3"
```

**Example for web-app**:
```yaml
services:
  web-app:
    build: .
    container_name: mac-automation-app
    ports:
      - "8080:5000"
    environment:
      - HOST_IP=host.docker.internal
      - HOST_SSH_PORT=22
      - HOST_USER=${HOST_USER}
      - HOST_PASSWORD=${HOST_PASSWORD}
      - SECRET_KEY=production_secret_key
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - monitoring
    logging:              # ← ADD THIS
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
```

#### **C. Convert Volume Mounts to Inline Configs**

**Replace** the volume mounts with configs for Prometheus, Loki, and Promtail:

**Prometheus** (was using volume):
```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--web.console.libraries=/usr/share/prometheus/console_libraries'
    - '--web.console.templates=/usr/share/prometheus/consoles'
  configs:                           # ← Changed from volumes
    - source: prometheus_config
      target: /etc/prometheus/prometheus.yml
  ports:
    - "19090:9090"
  networks:
    - monitoring
  logging:
    driver: "json-file"
    options:
      max-size: "50m"
      max-file: "3"
```

**Loki** (was using volume):
```yaml
loki:
  image: grafana/loki:latest
  container_name: loki
  ports:
    - "3100:3100"
  configs:                           # ← Changed from volumes
    - source: loki_config
      target: /etc/loki/local-config.yaml
  command: -config.file=/etc/loki/local-config.yaml
  networks:
    - monitoring
  logging:
    driver: "json-file"
    options:
      max-size: "50m"
      max-file: "3"
```

**Promtail** (was using volume):
```yaml
promtail:
  image: grafana/promtail:latest
  container_name: promtail
  configs:                           # ← Changed from volumes
    - source: promtail_config
      target: /etc/promtail/config.yml
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock  # Keep this one
  command: -config.file=/etc/promtail/config.yml
  networks:
    - monitoring
  logging:
    driver: "json-file"
    options:
      max-size: "50m"
      max-file: "3"
```

#### **D. Add Configs Section at the End**

Add this **after** the `networks:` section:

```yaml
networks:
  monitoring:
    driver: bridge

configs:
  prometheus_config:
    content: |
      global:
        scrape_interval: 15s
      
      scrape_configs:
        - job_name: 'mac_automation_app'
          static_configs:
            - targets: ['web-app:5000']
  
  loki_config:
    content: |
      auth_enabled: false
      
      server:
        http_listen_port: 3100
      
      common:
        ring:
          instance_addr: 127.0.0.1
          kvstore:
            store: inmemory
        replication_factor: 1
        path_prefix: /tmp/loki
      
      schema_config:
        configs:
          - from: 2020-10-24
            store: tsdb
            object_store: filesystem
            schema: v13
            index:
              prefix: index_
              period: 24h
      
      storage_config:
        filesystem:
          directory: /tmp/loki/chunks
      
      limits_config:
        allow_structured_metadata: false
        retention_period: 168h  # 7 days
        max_query_length: 721h  # 30 days
        ingestion_rate_mb: 50
        ingestion_burst_size_mb: 100
        per_stream_rate_limit: 50MB
        per_stream_rate_limit_burst: 100MB
      
      compactor:
        working_directory: /tmp/loki/compactor
        retention_enabled: true
        retention_delete_delay: 2h
        retention_delete_worker_count: 150
        delete_request_store: filesystem
  
  promtail_config:
    content: |
      server:
        http_listen_port: 9080
        grpc_listen_port: 0
      
      positions:
        filename: /tmp/positions.yaml
      
      clients:
        - url: http://loki:3100/loki/api/v1/push
      
      scrape_configs:
        - job_name: docker
          docker_sd_configs:
            - host: unix:///var/run/docker.sock
              refresh_interval: 5s
          relabel_configs:
            - source_labels: ['__meta_docker_container_name']
              regex: '/(.*)' 
              target_label: 'container'
            - source_labels: ['__meta_docker_container_log_stream']
              target_label: 'stream'
```

---

### **Step 3: Restart Docker Containers**

```bash
# Navigate to project directory
cd /Users/anandprakashmishra/Desktop/Danger/mac-automation-app

# Stop all containers
docker-compose down

# Start all containers with new configuration
docker-compose up -d

# Wait a few seconds for containers to start
sleep 5

# Verify all containers are running
docker ps
```

**Expected output**: You should see 5 containers running:
- `mac-automation-app`
- `prometheus`
- `grafana`
- `loki`
- `promtail`

---

### **Step 4: Verify Services**

```bash
# Test main app
curl http://localhost:8080

# Test Prometheus
curl http://localhost:19090/-/healthy

# Test Grafana
curl http://localhost:3000/api/health

# Check Loki logs
docker logs loki --tail 10
```

---

### **Step 5: Access Services**

Open in your browser:

1. **Main App**: http://localhost:8080
   - Login: `admin` / `password123`

2. **Grafana**: http://localhost:3000
   - Login: `admin` / `admin`

3. **Prometheus**: http://localhost:19090

---

### **Step 6: Set Up Grafana Dashboard**

1. Open Grafana: http://localhost:3000
2. Login with `admin` / `admin`
3. Go to **Connections** → **Data sources**
4. Click **Add data source**
5. Select **Prometheus**
6. Set URL: `http://prometheus:9090`
7. Click **Save & Test**
8. Go to **+** → **Import**
9. Upload `grafana-dashboard.json`
10. Click **Import**

---

## 🔍 Verification Checklist

After completing all steps, verify:

- [ ] Main app accessible at http://localhost:8080
- [ ] Prometheus accessible at http://localhost:19090
- [ ] Grafana accessible at http://localhost:3000
- [ ] All 5 containers running (`docker ps`)
- [ ] No port conflicts
- [ ] Logs rotating (check with `docker inspect mac-automation-app | grep LogConfig`)
- [ ] Loki compactor running (`docker logs loki | grep compactor`)

---

## 📊 Check Log Configuration

```bash
# Verify logging is configured
docker inspect mac-automation-app | grep -A 5 "LogConfig"

# Should show:
# "Type": "json-file"
# "max-file": "3"
# "max-size": "50m"
```

---

## 🛠️ Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8080
lsof -i :19090

# Kill the process or change ports in docker-compose.yml
```

### Container Won't Start

```bash
# Check logs
docker logs <container-name>

# Common issues:
# - Loki: Check schema version is v13
# - Prometheus: Check config syntax
# - Permissions: Make sure .env has correct credentials
```

### Config Not Updating

```bash
# Always do a full restart when changing configs
docker-compose down
docker-compose up -d

# NOT just restart:
# docker-compose restart  # ← This won't reload configs
```

---

## 📝 Quick Reference Commands

```bash
# Stop everything
docker-compose down

# Start everything
docker-compose up -d

# Restart specific service
docker-compose restart <service-name>

# View logs
docker logs <container-name>
docker logs -f <container-name>  # Follow logs

# Check running containers
docker ps

# Check log sizes
docker ps --format "table {{.Names}}\t{{.Size}}"

# Remove all containers and start fresh
docker-compose down -v
docker-compose up -d --build
```

---

## 🎯 Summary of Changes

| File | What Changed | Why |
|------|--------------|-----|
| `docker-compose.yml` | Ports, inline configs, logging | Fix conflicts, permissions, log limits |
| `.env` | Simplified to HOST_USER/PASSWORD | Easier configuration |
| `.env.example` | Template for .env | Documentation |
| Documentation files | Created guides | Help and reference |

---

## 📚 Documentation Files

All created documentation:
- `PORT_FIX.md` - Port conflict resolution
- `PROMETHEUS_FIX.md` - Prometheus Docker fix
- `GRAFANA_GUIDE.md` - Grafana usage guide
- `LOG_MANAGEMENT.md` - Log rotation guide
- `grafana-dashboard.json` - Dashboard template
- **THIS FILE** - Complete setup guide

---

## ✅ Final Checklist

After following all steps:

1. ✅ `.env` file created with your Mac credentials
2. ✅ `docker-compose.yml` updated with all changes
3. ✅ Containers restarted with `docker-compose down && docker-compose up -d`
4. ✅ All services accessible (8080, 3000, 19090)
5. ✅ Grafana dashboard imported
6. ✅ Log rotation verified

**You're all set!** 🎉
