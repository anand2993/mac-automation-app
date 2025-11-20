# Mac Automation App

A Dockerized application to control your Mac via a web interface, featuring a modern UI, secure login, and Prometheus/Grafana monitoring.

## Prerequisites

1.  **Docker Desktop** installed and running.
2.  **Remote Login (SSH)** enabled on your Mac:
    - Go to **System Settings** > **General** > **Sharing**.
    - Toggle **Remote Login** to **On**.
    - Note your username.

## Quick Start

1.  **Set Credentials**:
    You need to provide your Mac's username and password so the container can SSH into the host to run commands.
    
    Create a `.env` file in this directory (DO NOT COMMIT THIS FILE):
    ```bash
    HOST_USER=your_mac_username
    HOST_PASSWORD=your_mac_password
    ```

2.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```

3.  **Access the App**:
    - **Dashboard**: [http://localhost:5000](http://localhost:5000)
    - **Default Login**: `admin` / `password123` (Change this in `app/main.py`!)

4.  **Monitoring**:
    - **Grafana**: [http://localhost:3000](http://localhost:3000) (Login: `admin` / `admin`)
    - **Prometheus**: [http://localhost:9090](http://localhost:9090)
    - **Loki**: [http://localhost:3100](http://localhost:3100) (API endpoint)

5.  **View Logs in Grafana**:
    - Login to Grafana at [http://localhost:3000](http://localhost:3000)
    - Go to **Configuration** > **Data Sources** > **Add data source**
    - Select **Loki**
    - Set URL to `http://loki:3100`
    - Click **Save & Test**
    - Go to **Explore** and select **Loki** as the data source
    - Use queries like `{container="mac-automation-app"}` to view application logs
    - You can filter by log level: `{container="mac-automation-app"} |= "ERROR"`


## Azure DevOps Setup

1.  Create a new Pipeline in Azure DevOps.
2.  Select "Existing Azure Pipelines YAML file".
3.  Point to `azure-pipelines.yml` in this repository.
4.  **Important**: Add `HOST_USER` and `HOST_PASSWORD` as **Secret Variables** in the pipeline settings.

## Notes on Size
The application image itself is optimized using `python:3.9-alpine`. However, the full stack includes Prometheus and Grafana images which are larger. This is necessary to provide the requested monitoring capabilities.
