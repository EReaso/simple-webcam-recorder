# Docker Setup Guide

This guide explains how to run the Simple Webcam Recorder using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)
- USB webcam connected to your computer

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EReaso/simple-webcam-recorder.git
   cd simple-webcam-recorder
   ```

2. **Start the application:**
   ```bash
   docker-compose up
   ```

3. **Access the web interface:**
   Open your browser to `http://localhost:5000`

## Docker Commands

### Build and Run

```bash
# Build and start in foreground
docker-compose up

# Build and start in background (detached mode)
docker-compose up -d

# Rebuild if you made changes
docker-compose up --build
```

### View Logs

```bash
# View logs (all)
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs -f webcam-recorder
```

### Stop and Remove

```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Manual Docker Commands

If you prefer to use Docker directly without Docker Compose:

```bash
# Build the image
docker build -t webcam-recorder .

# Run the container
docker run -d \
  --name webcam-recorder \
  -p 5000:5000 \
  -v $(pwd)/recordings:/app/recordings \
  --device /dev/video0:/dev/video0 \
  webcam-recorder

# View logs
docker logs -f webcam-recorder

# Stop and remove
docker stop webcam-recorder
docker rm webcam-recorder
```

## Configuration

### Environment Variables

You can customize the application by creating a `.env` file:

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### Camera Device

The default configuration uses `/dev/video0`. If your webcam is on a different device:

1. Find your camera device:
   ```bash
   ls /dev/video*
   ```

2. Update `docker-compose.yml`:
   ```yaml
   devices:
     - /dev/video1:/dev/video0  # Change left side to your device
   ```

### Port Configuration

To use a different port, modify `docker-compose.yml`:

```yaml
ports:
  - "8080:5000"  # Access on http://localhost:8080
```

## Troubleshooting

### Camera Not Detected

**Problem:** "No camera detected" error in the container.

**Solutions:**
1. Verify your camera device exists:
   ```bash
   ls -la /dev/video*
   ```

2. Ensure the device is mapped in `docker-compose.yml`:
   ```yaml
   devices:
     - /dev/video0:/dev/video0
   ```

3. On Linux, grant permissions:
   ```bash
   sudo chmod 666 /dev/video0
   ```

### Permission Denied

**Problem:** Permission errors accessing the webcam.

**Solutions:**
1. Add your user to the video group:
   ```bash
   sudo usermod -aG video $USER
   ```
   Then log out and back in.

2. Run with privileged mode (not recommended for production):
   ```yaml
   privileged: true
   ```

3. Add specific group access in `docker-compose.yml`:
   ```yaml
   group_add:
     - video
   ```

### Recordings Not Persisted

**Problem:** Recordings disappear when container restarts.

**Solution:** Ensure the volume is properly mounted in `docker-compose.yml`:
```yaml
volumes:
  - ./recordings:/app/recordings
```

### Container Exits Immediately

**Problem:** Container starts and immediately stops.

**Solutions:**
1. Check the logs:
   ```bash
   docker-compose logs
   ```

2. Verify all required files exist:
   ```bash
   ls -la Dockerfile docker-compose.yml requirements.txt
   ```

## Platform-Specific Notes

### Linux

- Camera devices are typically `/dev/video0`, `/dev/video1`, etc.
- May need to add user to `video` group
- Works out of the box with Docker Engine

### macOS

- Docker Desktop required
- USB passthrough may have limitations
- Consider using host network mode if having connectivity issues

### Windows

- Docker Desktop with WSL2 backend required
- USB passthrough requires additional configuration
- See Docker Desktop documentation for USB device access

## Production Deployment

For production use, consider:

1. **Use a production WSGI server** (Gunicorn, uWSGI):
   ```dockerfile
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
   ```

2. **Set production environment**:
   ```yaml
   environment:
     - FLASK_ENV=production
     - DEBUG=False
   ```

3. **Add HTTPS** using a reverse proxy (nginx, Traefik)

4. **Implement authentication** for security

5. **Set resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

## Advanced Configuration

### Custom Network

```yaml
networks:
  webcam-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16
```

### Multiple Cameras

To use multiple cameras, run multiple containers:

```yaml
services:
  camera1:
    build: .
    ports:
      - "5000:5000"
    devices:
      - /dev/video0:/dev/video0
    environment:
      - CAMERA_INDEX=0

  camera2:
    build: .
    ports:
      - "5001:5000"
    devices:
      - /dev/video1:/dev/video0
    environment:
      - CAMERA_INDEX=0
```

## Support

For issues specific to Docker:
1. Check Docker and Docker Compose are up to date
2. Review container logs: `docker-compose logs -f`
3. Verify system resources are available
4. Check webcam is not in use by another application

For application issues, see the main [README.md](README.md) and [STREAMING.md](STREAMING.md).
