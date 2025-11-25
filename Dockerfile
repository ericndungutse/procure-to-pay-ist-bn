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

# Create a non root user and app directory(-m: create home dir, -r:  a system account)
RUN useradd -m -r appuser && mkdir /app && chown -R appuser /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set WOrking directory
WORKDIR /App

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non root user
USER appuser

# Expose port

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "procure-to-pay.wsgi:application"]

