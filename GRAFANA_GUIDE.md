# Grafana Monitoring Guide

## 📊 What is Grafana?

Grafana is a visualization and monitoring tool that helps you:
- Monitor your application's performance in real-time
- Create beautiful dashboards with graphs and charts
- Set up alerts for issues
- Track metrics like request counts, app usage, system status

---

## 🚀 Getting Started

### Step 1: Access Grafana

Open your browser and go to:
```
http://localhost:3000
```

### Step 2: Login

```
Username: admin
Password: admin
```

Grafana will ask you to change the password on first login. You can:
- Set a new password, OR
- Click "Skip" to keep using `admin/admin`

---

## 📈 Setting Up Your First Dashboard

### Step 1: Add Prometheus as a Data Source

1. **Click the hamburger menu** (☰) on the left
2. Go to **Connections** → **Data sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Configure:
   - **Name**: `Prometheus`
   - **URL**: `http://prometheus:9090` (use container name)
   - Leave other settings as default
6. Click **Save & Test**
   - ⚠️ Note: This will fail until you fix the Docker permissions issue
   - For now, you can use the app's `/metrics` endpoint directly

### Alternative: Use App Metrics Directly

Since Prometheus isn't running yet, you can create dashboards using the app's metrics endpoint:

1. Add data source → **Prometheus**
2. **URL**: `http://web-app:5000` (internal Docker network)
3. **HTTP Method**: GET
4. Click **Save & Test**

---

## 🎨 Create Your First Dashboard

### Option 1: Quick Dashboard (Manual)

1. Click **+** (plus icon) in the left sidebar
2. Select **Create Dashboard**
3. Click **Add visualization**
4. Select your **Prometheus** data source

### Add Request Count Panel

1. In the query editor, enter:
   ```promql
   app_request_count
   ```
2. Click **Run queries**
3. You should see your app's request metrics
4. **Panel title**: Change to "Total Requests"
5. **Visualization**: Choose "Time series" or "Stat"
6. Click **Apply**

### Add App Open Count Panel

1. Click **Add** → **Visualization**
2. Query:
   ```promql
   app_open_count
   ```
3. **Panel title**: "Apps Opened"
4. **Visualization**: "Bar chart" or "Stat"
5. Click **Apply**

### Add System Status Panel

1. Click **Add** → **Visualization**
2. Query:
   ```promql
   system_status
   ```
3. **Panel title**: "System Status"
4. **Visualization**: "Stat"
5. **Thresholds**: 
   - Red: 0 (Down)
   - Green: 1 (Up)
6. Click **Apply**

### Save Your Dashboard

1. Click the **Save** icon (💾) at the top
2. Name it: "Mac Automation Monitoring"
3. Click **Save**

---

## 📊 Pre-Built Dashboard (Recommended)

Let me create a dashboard JSON for you that you can import:

### Import Dashboard

1. Click **+** → **Import**
2. Upload the `grafana-dashboard.json` file (I'll create this below)
3. Select your Prometheus data source
4. Click **Import**

---

## 🔔 Setting Up Alerts

### Create an Alert for System Down

1. Open your dashboard
2. Click on the **System Status** panel
3. Click **Edit**
4. Go to the **Alert** tab
5. Click **Create alert rule from this panel**
6. Configure:
   - **Alert name**: "System Down Alert"
   - **Condition**: `system_status < 1`
   - **For**: 1m (alert after 1 minute)
7. Add notification channel (email, Slack, etc.)
8. Click **Save**

---

## 📱 Common Dashboards to Create

### 1. Application Performance Dashboard

**Panels to add:**
- Total Requests (Time series)
- Requests by Endpoint (Bar chart)
- Request Rate (Gauge)
- System Status (Stat)

### 2. App Usage Dashboard

**Panels to add:**
- Apps Opened Count (Stat)
- Apps Opened Over Time (Time series)
- Most Used Apps (Bar chart)
- Active Users (Stat)

### 3. System Health Dashboard

**Panels to add:**
- System Status (Stat with thresholds)
- Uptime (Stat)
- Error Rate (Time series)
- Response Time (Graph)

---

## 🎯 Useful Prometheus Queries

### Total Requests
```promql
sum(app_request_count)
```

### Requests Per Second
```promql
rate(app_request_count[5m])
```

### Requests by Endpoint
```promql
sum by (endpoint) (app_request_count)
```

### Requests by Method
```promql
sum by (method) (app_request_count)
```

### Apps Opened Count
```promql
sum(app_open_count)
```

### Most Opened Apps
```promql
topk(5, app_open_count)
```

### System Uptime
```promql
system_status
```

---

## 🔧 Troubleshooting

### "No data" in panels

**Cause**: Prometheus isn't running or no metrics yet

**Fix**:
1. Fix Docker Desktop permissions (see PORT_FIX.md)
2. Generate some traffic to your app:
   ```bash
   # Login to app
   curl -X POST http://localhost:8080/ -d "username=admin&password=password123"
   
   # Open an app
   curl -X POST http://localhost:8080/open-app \
     -H "Content-Type: application/json" \
     -d '{"app_name": "facetime"}' \
     -b cookies.txt
   ```
3. Check metrics endpoint:
   ```bash
   curl http://localhost:8080/metrics
   ```

### Can't connect to Prometheus

**Cause**: Docker permissions issue

**Fix**: See PORT_FIX.md for Docker Desktop file sharing setup

### Grafana won't load

**Check if container is running:**
```bash
docker ps | grep grafana
```

**Check logs:**
```bash
docker logs grafana
```

**Restart Grafana:**
```bash
docker-compose restart grafana
```

---

## 🎨 Dashboard Customization Tips

### Change Time Range
- Top right corner → Click time range (e.g., "Last 6 hours")
- Select custom range or preset

### Auto-Refresh
- Top right → Click refresh icon
- Select interval (5s, 10s, 30s, 1m, etc.)

### Dark/Light Theme
- Left sidebar → Profile icon
- Preferences → UI Theme

### Panel Options
- **Legend**: Show/hide metric labels
- **Tooltip**: Hover behavior
- **Axes**: Customize X/Y axis
- **Thresholds**: Color coding for values
- **Unit**: Display format (percent, bytes, etc.)

---

## 📚 Next Steps

### 1. Fix Prometheus Connection
Follow the Docker Desktop permissions fix in `PORT_FIX.md`

### 2. Add More Metrics to Your App
Edit `app/main.py` to add:
- Response time metrics
- Error counters
- Custom business metrics

Example:
```python
from prometheus_client import Histogram

REQUEST_DURATION = Histogram(
    'request_duration_seconds',
    'Request duration in seconds'
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    REQUEST_DURATION.observe(duration)
    return response
```

### 3. Explore Grafana Features
- **Variables**: Create dynamic dashboards
- **Annotations**: Mark important events
- **Playlists**: Rotate through dashboards
- **Snapshots**: Share dashboard state
- **Export**: Save as PDF or image

---

## 🌟 Pro Tips

1. **Use Variables**: Create dropdown filters for endpoints, apps, etc.
2. **Set Up Alerts**: Get notified before issues become critical
3. **Use Folders**: Organize dashboards by category
4. **Share Dashboards**: Export JSON and version control them
5. **Use Templates**: Import community dashboards from grafana.com

---

## 📖 Quick Reference

| Action | How To |
|--------|--------|
| Add Panel | Dashboard → Add → Visualization |
| Edit Panel | Click panel title → Edit |
| Duplicate Panel | Panel menu → More → Duplicate |
| Move Panel | Drag panel by title bar |
| Resize Panel | Drag bottom-right corner |
| Delete Panel | Panel menu → More → Remove |
| Save Dashboard | Top toolbar → Save icon (💾) |
| Share Dashboard | Top toolbar → Share icon |
| Export Dashboard | Dashboard settings → JSON Model |

---

## 🔗 Useful Links

- **Grafana Docs**: https://grafana.com/docs/grafana/latest/
- **Prometheus Queries**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Dashboard Examples**: https://grafana.com/grafana/dashboards/

---

## 🎯 Your Current Metrics

Your Mac Automation App exposes these metrics at `http://localhost:8080/metrics`:

1. **app_request_count** - Total requests by method and endpoint
2. **app_open_count** - Number of times each app was opened
3. **system_status** - System health (1=Up, 0=Down)

You can view them directly:
```bash
curl http://localhost:8080/metrics
```

Example output:
```
# HELP app_request_count Total app requests
# TYPE app_request_count counter
app_request_count{endpoint="/",method="GET"} 5.0
app_request_count{endpoint="/dashboard",method="GET"} 3.0

# HELP app_open_count Number of times an app switch was toggled
# TYPE app_open_count counter
app_open_count{app_name="facetime"} 2.0
app_open_count{app_name="whatsapp"} 1.0

# HELP system_status System status (1=Up, 0=Down)
# TYPE system_status gauge
system_status 1.0
```
