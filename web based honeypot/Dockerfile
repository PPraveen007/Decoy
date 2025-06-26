# Use Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY honeypot.py .

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data

# # Create non-root user for security
# RUN useradd -m -s /bin/bash honeypot && \
#     chown -R honeypot:honeypot /app

# # Switch to non-root user
# USER honeypot

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Run the application
CMD ["python", "honeypot.py"]