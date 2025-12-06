FROM python:3.11-slim

# Install system dependencies for OpenCV
# Using opencv-python-headless for better multi-arch compatibility (x86_64 and ARM)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libgstreamer1.0-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Create recordings directory
RUN mkdir -p recordings

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application with Gunicorn (production WSGI server)
# The entrypoint script reads WORKERS env variable to configure worker count
CMD ["./entrypoint.sh"]
