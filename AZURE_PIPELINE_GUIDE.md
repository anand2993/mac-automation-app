# Azure Pipeline Guide - Complete Deployment

## 🎯 Overview

The Azure Pipeline now performs a **complete stop, rebuild, and restart** of all Docker containers with comprehensive verification.

---

## 📋 Pipeline Steps

### **Step 1: Show Current State** 📊
- Shows currently running containers
- Lists existing Docker images
- Helps track what's about to change

### **Step 2: Stop All Containers** 🛑
- Runs `docker-compose down`
- Stops and removes all containers
- Verifies containers are stopped

### **Step 3: Clean Up Old Images** 🧹
- Removes old application image
- Prunes dangling images
- Frees up disk space

### **Step 4: Build Docker Images** 🔨
- Builds with `--no-cache` flag (fresh build)
- Ensures latest code is used
- Shows newly built images

### **Step 5: Verify Build** ✅
- Confirms image was built successfully
- Fails pipeline if build didn't work

### **Step 6: Start All Containers** 🚀
- Runs `docker-compose up -d`
- Starts all 5 containers
- Waits 10 seconds for startup

### **Step 7: Verify Containers Running** ✅
- Checks all 5 containers are running
- Fails if any container is missing
- Lists: web-app, prometheus, grafana, loki, promtail

### **Step 8: Health Checks** 🏥
- Tests web app at port 8080
- Tests Prometheus at port 19090
- Tests Grafana at port 3000
- Tests Loki at port 3100

### **Step 9: Show Container Logs** 📝
- Displays recent logs from each container
- Helps with debugging
- Shows last 10-20 lines per container

### **Step 10: Verify Log Configuration** 📊
- Confirms 50MB log rotation is configured
- Checks log driver settings

### **Step 11: Deployment Summary** 🎉
- Shows final status
- Lists all service URLs
- Displays container status table

---

## 🚀 How to Use

### **1. Set Up Azure DevOps Variables**

Before running the pipeline, configure these **secret variables** in Azure DevOps:

1. Go to your Azure DevOps project
2. Navigate to **Pipelines** → **Library**
3. Create a new **Variable Group** named `mac-automation-secrets`
4. Add these variables:
   - `HOST_USER` = `anandprakashmishra`
   - `HOST_PASSWORD` = `your_mac_password` (mark as secret 🔒)

5. Link the variable group to your pipeline:
   - Edit `azure-pipelines.yml`
   - Add at the top:
   ```yaml
   variables:
   - group: mac-automation-secrets
   ```

**OR** add variables directly to the pipeline:

1. Go to **Pipelines** → Select your pipeline
2. Click **Edit** → **Variables**
3. Add:
   - `HOST_USER` = `anandprakashmishra`
   - `HOST_PASSWORD` = `your_mac_password` (check "Keep this value secret")

---

### **2. Trigger the Pipeline**

The pipeline triggers automatically on:
- ✅ Push to `main` branch
- ✅ Pull request to `main` branch

**Manual trigger:**
1. Go to **Pipelines**
2. Select **mac-automation-app**
3. Click **Run pipeline**
4. Select branch: `main`
5. Click **Run**

---

### **3. Monitor the Pipeline**

Watch the pipeline execution:

```
📊 Show Current State          ← See what's running now
🛑 Stop All Containers         ← Stops everything
🧹 Clean Up Old Images         ← Removes old builds
🔨 Build Docker Images         ← Fresh build
✅ Verify Build                ← Confirms build worked
🚀 Start All Containers        ← Starts everything
✅ Verify All Containers       ← Checks all running
🏥 Health Checks               ← Tests each service
📝 Show Container Logs         ← Shows recent logs
📊 Verify Log Configuration    ← Confirms log rotation
🎉 Deployment Summary          ← Final status
```

---

## 📊 Expected Output

### Successful Pipeline Run

```
====================================
🎉 DEPLOYMENT SUCCESSFUL!
====================================

Services accessible at:
  • Web App:    http://localhost:8080
  • Grafana:    http://localhost:3000
  • Prometheus: http://localhost:19090
  • Loki:       http://localhost:3100

Container Status:
NAMES                STATUS              PORTS
mac-automation-app   Up 15 seconds       0.0.0.0:8080->5000/tcp
prometheus           Up 15 seconds       0.0.0.0:19090->9090/tcp
grafana              Up 15 seconds       0.0.0.0:3000->3000/tcp
loki                 Up 15 seconds       0.0.0.0:3100->3100/tcp
promtail             Up 15 seconds       

====================================
```

---

## 🔧 Pipeline Configuration

### Current Settings

```yaml
trigger:
  - main                    # Auto-trigger on main branch

pool:
  name: 'Default'          # Self-hosted agent pool

variables:
  imageName: 'mac-automation-app'
  composeFile: 'docker-compose.yml'
```

### Environment Variables Used

```yaml
env:
  HOST_USER: $(HOST_USER)           # From Azure DevOps variables
  HOST_PASSWORD: $(HOST_PASSWORD)   # From Azure DevOps variables (secret)
```

---

## 🛠️ Customization Options

### Change Build Behavior

**Build with cache** (faster but may use old layers):
```yaml
docker-compose -f $(composeFile) build
```

**Build without cache** (slower but guaranteed fresh):
```yaml
docker-compose -f $(composeFile) build --no-cache
```

### Adjust Wait Times

```yaml
# Current: 10 seconds
sleep 10

# For slower machines:
sleep 20

# For faster machines:
sleep 5
```

### Add More Health Checks

```yaml
# Add custom endpoint check
echo "Checking custom endpoint..."
curl -f http://localhost:8080/api/status && echo "✅ API is healthy"
```

---

## 🐛 Troubleshooting

### Pipeline Fails at "Stop All Containers"

**Cause**: Containers might not exist yet
**Solution**: Already handled with `continueOnError: true`

### Pipeline Fails at "Build Docker Images"

**Possible causes**:
1. Syntax error in Dockerfile
2. Missing dependencies in requirements.txt
3. Network issues pulling base images

**Check**:
```bash
# Run locally to see detailed error
docker-compose build --no-cache
```

### Pipeline Fails at "Verify All Containers Running"

**Possible causes**:
1. Container crashed on startup
2. Port conflicts
3. Configuration errors

**Check logs**:
```bash
docker logs <container-name>
```

### Health Checks Fail

**Possible causes**:
1. Services not ready yet (increase sleep time)
2. Port conflicts
3. Service crashed

**Fix**:
```yaml
# Increase wait time before health checks
sleep 15  # Instead of 5
```

---

## 📈 Pipeline Optimization

### Speed Up Builds

1. **Use Docker layer caching**:
   ```yaml
   docker-compose build  # Remove --no-cache
   ```

2. **Skip image cleanup**:
   ```yaml
   # Comment out Step 3
   ```

3. **Reduce wait times**:
   ```yaml
   sleep 5  # Instead of 10
   ```

### Add Notifications

Add email notification on failure:

```yaml
- task: SendEmail@1
  condition: failed()
  inputs:
    To: 'your@email.com'
    Subject: 'Pipeline Failed: $(Build.BuildNumber)'
    Body: 'Deployment failed. Check logs.'
```

### Add Slack Notification

```yaml
- task: SlackNotification@1
  inputs:
    SlackApiToken: '$(SlackToken)'
    MessageAuthor: 'Azure Pipeline'
    NotificationText: 'Deployment completed successfully!'
```

---

## 🔐 Security Best Practices

### ✅ DO:
- Store `HOST_PASSWORD` as a secret variable
- Use Variable Groups for sensitive data
- Enable "Keep this value secret" checkbox
- Use Azure Key Vault for production

### ❌ DON'T:
- Hardcode passwords in `azure-pipelines.yml`
- Commit `.env` file to Git
- Share pipeline variables publicly
- Log sensitive information

---

## 📊 Monitoring Pipeline Performance

### Track Build Times

Add timing to each step:

```yaml
- script: |
    start_time=$(date +%s)
    docker-compose build --no-cache
    end_time=$(date +%s)
    echo "Build took $((end_time - start_time)) seconds"
  displayName: '🔨 Build Docker Images'
```

### Save Build Artifacts

```yaml
- task: PublishBuildArtifacts@1
  inputs:
    PathtoPublish: 'logs/'
    ArtifactName: 'container-logs'
```

---

## 🚀 Advanced Features

### Parallel Builds

Build multiple services in parallel:

```yaml
- script: |
    docker-compose build --parallel
  displayName: 'Build Images (Parallel)'
```

### Conditional Deployment

Deploy only on specific branches:

```yaml
- script: |
    docker-compose up -d
  displayName: 'Deploy to Production'
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
```

### Rollback on Failure

```yaml
- script: |
    echo "Deployment failed, rolling back..."
    docker-compose down
    docker-compose up -d --no-build  # Use previous images
  displayName: 'Rollback on Failure'
  condition: failed()
```

---

## 📝 Pipeline Execution Flow

```
┌─────────────────────────────────────────┐
│  Git Push to main branch                │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Azure Pipeline Triggered               │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 1: Show Current State             │
│  - List running containers              │
│  - Show existing images                 │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 2: Stop All Containers            │
│  - docker-compose down                  │
│  - Verify stopped                       │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 3: Clean Up Old Images            │
│  - Remove old app image                 │
│  - Prune dangling images                │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 4: Build Docker Images            │
│  - docker-compose build --no-cache      │
│  - Fresh build with latest code         │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 5: Verify Build                   │
│  - Check image exists                   │
│  - Fail if build didn't work            │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 6: Start All Containers           │
│  - docker-compose up -d                 │
│  - Wait 10 seconds                      │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 7: Verify Containers Running      │
│  - Check all 5 containers               │
│  - Fail if any missing                  │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 8: Health Checks                  │
│  - Test web app (8080)                  │
│  - Test Prometheus (19090)              │
│  - Test Grafana (3000)                  │
│  - Test Loki (3100)                     │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 9: Show Container Logs            │
│  - Display recent logs                  │
│  - Help with debugging                  │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 10: Verify Log Configuration      │
│  - Check 50MB limit                     │
│  - Confirm rotation                     │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Step 11: Deployment Summary            │
│  - Show service URLs                    │
│  - Display container status             │
│  - Success message                      │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  ✅ DEPLOYMENT COMPLETE                 │
└─────────────────────────────────────────┘
```

---

## ✅ Checklist Before Running Pipeline

- [ ] Azure DevOps agent is running (`./run.sh`)
- [ ] `HOST_USER` variable is set in Azure DevOps
- [ ] `HOST_PASSWORD` variable is set (as secret)
- [ ] Code is pushed to `main` branch
- [ ] `.env` file exists locally (for testing)
- [ ] No port conflicts (8080, 3000, 19090, 3100)
- [ ] Docker is running on the agent machine

---

## 🎉 Summary

The pipeline now:
- ✅ Stops all containers completely
- ✅ Cleans up old images
- ✅ Builds fresh images with latest code
- ✅ Starts all containers
- ✅ Verifies everything is running
- ✅ Performs health checks
- ✅ Shows comprehensive logs
- ✅ Confirms log rotation is configured

**Total pipeline time**: ~2-5 minutes (depending on build cache)

---

## 📚 Related Documentation

- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Complete setup instructions
- [LOG_MANAGEMENT.md](./LOG_MANAGEMENT.md) - Log rotation details
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Quick commands
