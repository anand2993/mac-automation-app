# Grafana Log Viewing Guide

## Quick Setup

After running `docker-compose up --build`, your logs are automatically collected by **Promtail** and stored in **Loki**.

## Viewing Logs in Grafana

1. **Access Grafana**: Open [http://localhost:3000](http://localhost:3000)
   - Username: `admin`
   - Password: `admin`

2. **Add Loki Data Source**:
   - Navigate to **Configuration** (⚙️) > **Data Sources**
   - Click **Add data source**
   - Select **Loki**
   - Set URL: `http://loki:3100`
   - Click **Save & Test** (should show green success)

3. **Explore Logs**:
   - Click **Explore** (🧭) in the left sidebar
   - Select **Loki** from the dropdown at the top
   - Use LogQL queries to filter logs:

### Example LogQL Queries

```logql
# All logs from the web app
{container="mac-automation-app"}

# Only ERROR level logs
{container="mac-automation-app"} |= "ERROR"

# Login-related logs
{container="mac-automation-app"} |= "login"

# SSH command logs
{container="mac-automation-app"} |= "SSH"

# All containers
{container=~".+"}
```

## Log Levels
The application logs at different levels:
- **INFO**: Normal operations (logins, app launches)
- **WARNING**: Failed login attempts, unknown apps
- **ERROR**: SSH failures, configuration issues

## Creating a Dashboard
1. Go to **Dashboards** > **New Dashboard**
2. Add a **Logs** panel
3. Select **Loki** as data source
4. Use queries like `{container="mac-automation-app"}`
5. Save the dashboard
