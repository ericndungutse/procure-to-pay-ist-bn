# Stage 1: Build Stage
FROM python:3.12-slim AS builder

# Create App Directory
RUN mkdir /app

# SET WORKING DIRECTORY
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip

# Copy Packages requirements.txt
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Stage
FROM python:3.12-slim

# Install Supervisor to run both the server and consumer file
RUN apt-get update && apt-get install -y supervisor \
    && rm -rf /var/lib/apt/lists/* && useradd -m -r appuser && mkdir /app && chown -R appuser /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set WOrking directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# **ADD SUPERVISOR CONFIGURATION FILE**
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non root user
USER appuser

# Expose port
EXPOSE 8000

# Start the application using Gunicorn
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

