# Stage 1: Build
FROM python:3.9-alpine as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-alpine

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app ./app

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app/main.py"]
