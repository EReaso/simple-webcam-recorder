#!/bin/bash
# Entrypoint script for production deployment with Gunicorn
# Reads WORKERS environment variable to configure the number of workers

# Default values
WORKERS=${WORKERS:-4}
BIND=${HOST:-0.0.0.0}:${PORT:-5000}
TIMEOUT=${TIMEOUT:-120}

echo "Starting Gunicorn with $WORKERS workers on $BIND (timeout: ${TIMEOUT}s)"

# Start Gunicorn with configured workers
exec gunicorn --bind "$BIND" --workers "$WORKERS" --timeout "$TIMEOUT" wsgi:app
