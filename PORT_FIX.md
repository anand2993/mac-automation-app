# Port Conflict Resolution - FIXED ✅

## ✅ Current Status

### Working Services:
- ✅ **Main Application**: http://localhost:8080 (WORKING!)
- ✅ **Grafana Dashboard**: http://localhost:3000 (WORKING!)

### Pending Services (Docker Desktop Permission Issue):
- ⚠️ **Prometheus**: Needs Docker Desktop file sharing permission
- ⚠️ **Loki**: Needs Docker Desktop file sharing permission  
- ⚠️ **Promtail**: Needs Docker Desktop file sharing permission

## Problem Solved
Port 5000 was in use by macOS ControlCenter (AirPlay Receiver).

## Solution Applied
Changed the external port mapping from `5000:5000` to `8080:5000` in `docker-compose.yml`.
Changed Prometheus port from `9090:9090` to `19090:9090` to avoid Electron conflict.

## How to Access the Application

### Main Application ✅
```
http://localhost:8080
```
**Login credentials**: admin / password123

### Prometheus Metrics ✅
```
http://localhost:8080/metrics
```

### Grafana Dashboard ✅
```
http://localhost:3000
```
**Default credentials**: admin / admin

### Prometheus UI (After fixing permissions)
```
http://localhost:19090
```

### Loki (Logs) (After fixing permissions)
```
http://localhost:3100
```

---

## 🔧 Fix Docker Desktop File Sharing Permissions

The monitoring services (Prometheus, Loki, Promtail) can't start because Docker Desktop doesn't have permission to access the Desktop folder.

### Option 1: Enable File Sharing in Docker Desktop (Recommended)

1. **Open Docker Desktop**
2. Click the **Settings** (gear icon)
3. Go to **Resources** → **File Sharing**
4. Add the path: `/Users/anandprakashmishra/Desktop`
5. Click **Apply & Restart**
6. Run: `docker-compose up -d`

### Option 2: Move Project to a Different Location

Move the project out of the Desktop folder:

```bash
# Create a projects directory
mkdir -p ~/projects

# Move the project
mv ~/Desktop/Danger/mac-automation-app ~/projects/

# Navigate to new location
cd ~/projects/mac-automation-app

# Restart containers
docker-compose down
docker-compose up -d
```

### Option 3: Use Absolute Paths in docker-compose.yml

Update the volume mounts to use `$PWD`:

```yaml
prometheus:
  volumes:
    - ${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml

loki:
  volumes:
    - ${PWD}/loki-config.yml:/etc/loki/local-config.yaml

promtail:
  volumes:
    - ${PWD}/promtail-config.yml:/etc/promtail/config.yml
```

---

## Current Port Mappings

| Service | External Port | Internal Port | Status |
|---------|--------------|---------------|---------|
| Web App | 8080 | 5000 | ✅ Running |
| Grafana | 3000 | 3000 | ✅ Running |
| Prometheus | 19090 | 9090 | ⚠️ Permission Issue |
| Loki | 3100 | 3100 | ⚠️ Permission Issue |
| Promtail | - | - | ⚠️ Permission Issue |

---

## Verify the Fix

### Check running containers
```bash
docker ps
```

### Test the main application
```bash
curl http://localhost:8080
```

### Check container logs
```bash
# Main app logs
docker logs mac-automation-app

# Grafana logs
docker logs grafana

# Prometheus logs (after fixing permissions)
docker logs prometheus
```

---

## Alternative Solutions (if needed)

### Option 1: Disable AirPlay Receiver on macOS (for port 5000)
1. Open **System Settings**
2. Go to **General** → **AirDrop & Handoff**
3. Turn off **AirPlay Receiver**
4. Port 5000 will be freed up

### Option 2: Kill the Process Using Port 5000
```bash
# Find the process
lsof -i :5000

# Kill it (replace PID with actual process ID)
kill -9 <PID>
```

---

## Troubleshooting

### If port 8080 is also in use
```bash
# Check what's using port 8080
lsof -i :8080

# Change to another port (e.g., 8081)
# Edit docker-compose.yml and change "8080:5000" to "8081:5000"
```

### Restart specific service
```bash
docker-compose restart web-app
docker-compose restart grafana
```

### Complete restart
```bash
docker-compose down
docker-compose up -d
```

---

## Update Azure Pipeline

Your Azure Pipeline should now reference port 8080:

```yaml
- script: |
    echo "Testing application..."
    curl http://localhost:8080
  displayName: 'Test Application'
```

---

## Quick Commands

```bash
# Check what's running
docker ps

# View logs
docker-compose logs -f web-app

# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# Start everything
docker-compose up -d
```
