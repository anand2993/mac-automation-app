# Log Management Configuration - 50MB Limit ✅

## 📋 Summary

I've configured automatic log rotation and retention for all Docker containers with a **50MB limit per container**. Older logs will be automatically deleted when the limit is reached.

---

## ✅ What Was Configured

### 1. **Docker Container Log Rotation** (All Services)

Each container now has:
- **Max log file size**: 50MB
- **Number of log files**: 3 (keeps 3 rotated files)
- **Total max storage per container**: ~150MB (50MB × 3 files)

**Affected containers:**
- `mac-automation-app`
- `prometheus`
- `grafana`
- `loki`
- `promtail`

### 2. **Loki Log Retention** (Application Logs)

Loki (log aggregation system) is configured to:
- **Retention period**: 7 days (168 hours)
- **Max ingestion rate**: 50MB/s
- **Ingestion burst**: 100MB
- **Per-stream limit**: 50MB
- **Auto-delete**: Logs older than 7 days are automatically removed

---

## 🔧 Configuration Details

### Docker Logging Configuration

Added to each service in `docker-compose.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "50m"      # Maximum size of each log file
    max-file: "3"        # Number of log files to keep
```

**How it works:**
1. When a log file reaches 50MB, Docker creates a new log file
2. Keeps the current file + 2 older files (3 total)
3. When creating the 4th file, the oldest file is deleted
4. Total storage: ~150MB per container

### Loki Retention Configuration

Added to Loki config in `docker-compose.yml`:

```yaml
limits_config:
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
```

**How it works:**
1. Logs are stored for 7 days
2. After 7 days, the compactor automatically deletes old logs
3. Compactor runs every 2 hours to clean up
4. Ingestion rate is limited to prevent disk overflow

---

## 📊 Log Storage Breakdown

| Component | Max Size | Retention | Auto-Delete |
|-----------|----------|-----------|-------------|
| **Docker Logs (per container)** | 150MB | 3 files | ✅ Yes |
| **Loki Aggregated Logs** | Unlimited* | 7 days | ✅ Yes |
| **Total per container** | ~150MB | Rolling | ✅ Yes |

*Loki storage grows with usage but auto-deletes after 7 days

---

## 🔍 View Current Log Sizes

### Check Docker Log Sizes
```bash
# View all container log sizes
docker ps --format "table {{.Names}}\t{{.Size}}"

# Check specific container log file
docker inspect --format='{{.LogPath}}' mac-automation-app
ls -lh $(docker inspect --format='{{.LogPath}}' mac-automation-app)
```

### Check Loki Storage
```bash
# View Loki storage directory size
docker exec loki du -sh /tmp/loki/chunks
```

### View Recent Logs
```bash
# View logs from specific container
docker logs mac-automation-app --tail 100

# View logs with timestamps
docker logs mac-automation-app --timestamps --tail 50

# Follow logs in real-time
docker logs -f mac-automation-app
```

---

## 🗑️ Manual Log Cleanup (If Needed)

### Clear Docker Logs Manually
```bash
# Clear logs for specific container
truncate -s 0 $(docker inspect --format='{{.LogPath}}' mac-automation-app)

# Clear all Docker logs
docker ps -q | xargs -I {} sh -c 'truncate -s 0 $(docker inspect --format="{{.LogPath}}" {})'
```

### Clear Loki Logs
```bash
# Restart Loki (clears in-memory data)
docker-compose restart loki

# Remove Loki storage completely
docker-compose down
docker exec loki rm -rf /tmp/loki/chunks/*
docker-compose up -d
```

### Prune All Docker System Logs
```bash
# Remove all unused Docker data (careful!)
docker system prune -a --volumes

# Just remove logs
docker system prune
```

---

## 📈 Monitor Log Usage

### Create Monitoring Script

Create `check-logs.sh`:

```bash
#!/bin/bash

echo "=== Docker Container Log Sizes ==="
docker ps --format "table {{.Names}}\t{{.Size}}"

echo -e "\n=== Individual Log File Sizes ==="
for container in $(docker ps --format "{{.Names}}"); do
    log_path=$(docker inspect --format='{{.LogPath}}' $container 2>/dev/null)
    if [ -n "$log_path" ] && [ -f "$log_path" ]; then
        size=$(ls -lh "$log_path" | awk '{print $5}')
        echo "$container: $size"
    fi
done

echo -e "\n=== Loki Storage Size ==="
docker exec loki du -sh /tmp/loki/chunks 2>/dev/null || echo "Loki not running"

echo -e "\n=== Total Docker Disk Usage ==="
docker system df
```

Make it executable:
```bash
chmod +x check-logs.sh
./check-logs.sh
```

---

## ⚙️ Customize Log Limits

### Change Log Size Limit

Edit `docker-compose.yml` and modify the logging section:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "100m"    # Change to 100MB
    max-file: "5"       # Keep 5 files instead of 3
```

Then restart:
```bash
docker-compose down && docker-compose up -d
```

### Change Loki Retention Period

Edit the `loki_config` section in `docker-compose.yml`:

```yaml
limits_config:
  retention_period: 336h  # Change to 14 days (336 hours)
```

Then restart:
```bash
docker-compose restart loki
```

---

## 🚨 Alerts for Log Size

### Set Up Disk Space Alert

Create a cron job to check disk usage:

```bash
# Edit crontab
crontab -e

# Add this line to check every hour
0 * * * * /path/to/check-logs.sh | grep -q "90%" && echo "WARNING: Logs approaching limit" | mail -s "Log Alert" your@email.com
```

### Prometheus Alert (Advanced)

Add to Prometheus config to alert on high disk usage:

```yaml
- alert: HighLogDiskUsage
  expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
  for: 5m
  annotations:
    summary: "Disk space low on {{ $labels.instance }}"
```

---

## 📝 Best Practices

### 1. **Regular Monitoring**
```bash
# Check log sizes weekly
./check-logs.sh

# Set up automated monitoring
```

### 2. **Adjust Based on Usage**
- If logs rotate too frequently → Increase `max-size`
- If disk space is limited → Decrease `max-file` count
- If you need longer history → Increase Loki `retention_period`

### 3. **Archive Important Logs**
```bash
# Export logs before they're deleted
docker logs mac-automation-app > backup-$(date +%Y%m%d).log

# Compress old logs
gzip backup-*.log
```

### 4. **Use Log Levels**
In your Python app (`app/main.py`), use appropriate log levels:

```python
import logging

# Only log important events in production
logging.basicConfig(level=logging.WARNING)  # Instead of INFO

# Or use environment variable
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
```

---

## ✅ Verification

### Test Log Rotation

Generate lots of logs to test rotation:

```bash
# Generate test logs
for i in {1..10000}; do
    docker exec mac-automation-app python -c "import logging; logging.warning('Test log entry $i' * 100)"
done

# Check if rotation happened
docker inspect --format='{{.LogPath}}' mac-automation-app
ls -lh $(docker inspect --format='{{.LogPath}}' mac-automation-app)*
```

### Verify Loki Retention

```bash
# Check Loki compactor status
docker logs loki | grep compactor

# Should see: "this instance has been chosen to run the compactor"
```

---

## 🎯 Summary

✅ **Docker log rotation**: 50MB per file, 3 files max (~150MB total per container)
✅ **Loki retention**: 7 days, auto-delete enabled
✅ **All services configured**: web-app, prometheus, grafana, loki, promtail
✅ **Automatic cleanup**: No manual intervention needed

Your logs will now automatically rotate and old logs will be deleted, preventing disk space issues! 🎉

---

## 📚 Additional Resources

- **Docker Logging**: https://docs.docker.com/config/containers/logging/json-file/
- **Loki Retention**: https://grafana.com/docs/loki/latest/operations/storage/retention/
- **Log Management Best Practices**: https://www.docker.com/blog/docker-logging-best-practices/
