# Simple Webcam Recorder

A plug-and-play Flask web application for recording and streaming USB webcam video. Features a modern Bootstrap 5 web interface with Docker-based deployment.

## Features

- 🎥 **Live webcam streaming** - Real-time video stream from USB camera
- 🔴 **Video recording** - Start/stop recording with one click
- 🎨 **Modern UI** - Clean Bootstrap 5 interface
- ⚙️ **Configurable** - Customize camera settings, resolution, FPS, and more
- 📁 **Recording management** - View list of recorded videos
- 🐳 **Docker-based** - Consistent deployment across x86_64 and ARM architectures
- 🔧 **Multi-arch support** - Native support for Raspberry Pi and ARM-based systems

## Requirements

- Docker and Docker Compose
- USB webcam or Raspberry Pi Camera Module
- Linux, macOS, or Windows with Docker installed

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EReaso/simple-webcam-recorder.git
   cd simple-webcam-recorder
   ```

2. **Start the application:**
   ```bash
   docker-compose up -d
   ```

3. **Access the web interface:**
   Open your browser to `http://localhost:5000`

That's it! The application runs in production mode by default with a randomly generated secret key for each startup.

## Configuration

The application works out-of-the-box with sensible defaults. If you need to customize settings, you can:

### Option 1: Edit docker-compose.yml (Recommended)

Edit the `environment` section in `docker-compose.yml`:

```yaml
environment:
  - CAMERA_INDEX=0          # Camera device (0 for default)
  - CAMERA_WIDTH=640        # Video width
  - CAMERA_HEIGHT=480       # Video height
  - CAMERA_FPS=30           # Frames per second
  - WORKERS=4               # Gunicorn workers (use 2-3 for Raspberry Pi)
```

### Option 2: Use a .env file

Copy the example file and modify it:

```bash
cp .env.example .env
nano .env
```

Available settings:
- `CAMERA_INDEX` - Camera device index (default: 0)
- `CAMERA_WIDTH` - Video width in pixels (default: 640)
- `CAMERA_HEIGHT` - Video height in pixels (default: 480)
- `CAMERA_FPS` - Frames per second (default: 30)
- `VIDEO_CODEC` - Video codec (default: mp4v)
- `VIDEO_FORMAT` - Output file format (default: mp4)
- `WORKERS` - Number of Gunicorn worker processes (default: 4)

## Platform-Specific Notes

### Linux
On Linux, you may need to adjust the webcam device in `docker-compose.yml` if your camera is not at `/dev/video0`:

```bash
# Find your webcam device
ls /dev/video*

# Update docker-compose.yml devices section
devices:
  - /dev/video1:/dev/video0  # Replace /dev/video1 with your device
```

### Raspberry Pi and ARM Systems

The application works out-of-the-box on ARM systems including Raspberry Pi. For optimal performance on devices with limited resources:

1. **Reduce worker count** in `docker-compose.yml`:
   ```yaml
   environment:
     - WORKERS=2  # or 3 for better performance on limited resources
   ```

2. **Lower resolution settings** if needed:
   ```yaml
   environment:
     - CAMERA_WIDTH=320
     - CAMERA_HEIGHT=240
     - CAMERA_FPS=15
   ```

The unified Docker image automatically uses `opencv-python-headless` which is optimized for both x86_64 and ARM architectures.

### macOS and Windows

On macOS and Windows, webcam device mapping may differ from Linux. Refer to Docker documentation for your platform:
- macOS: [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/)
- Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/)

## Docker Commands

```bash
# Start in foreground (see logs in terminal)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

## Running as a System Service

To automatically start the webcam recorder on boot:

### 1. Install to a permanent location
```bash
sudo mkdir -p /opt/simple-webcam-recorder
cd /opt/simple-webcam-recorder
sudo git clone https://github.com/EReaso/simple-webcam-recorder.git .
```

### 2. Create systemd service file
```bash
sudo nano /etc/systemd/system/webcam-recorder.service
```

Add the following content:
```ini
[Unit]
Description=Simple Webcam Recorder (Docker)
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/simple-webcam-recorder
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

### 3. Enable and start the service
```bash
sudo systemctl daemon-reload
sudo systemctl enable webcam-recorder.service
sudo systemctl start webcam-recorder.service
sudo systemctl status webcam-recorder.service
```

### 4. Manage the service
```bash
# View logs
sudo journalctl -u webcam-recorder.service -f

# Stop the service
sudo systemctl stop webcam-recorder.service

# Restart the service
sudo systemctl restart webcam-recorder.service
```

## Performance Tuning

### Worker Count

Adjust the number of Gunicorn workers based on your hardware:

- **Recommended formula:** `(2 × CPU_cores) + 1`
- For a 4-core CPU: 9 workers
- For a 2-core CPU: 5 workers
- **For Raspberry Pi:** 2-3 workers (limited resources)

Edit `docker-compose.yml`:
```yaml
environment:
  - WORKERS=9  # Adjust based on your CPU
```

### Port Configuration

To change the port, edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Changes external port to 8080
```

## Security

- **SECRET_KEY**: Automatically generated randomly on each startup. No manual configuration needed.
- **Production mode**: Enabled by default with debug mode disabled.
- **Container isolation**: The application runs in an isolated Docker container.

## Troubleshooting

### Camera Not Detected

```bash
# Check available video devices
ls /dev/video*

# Update docker-compose.yml with the correct device
devices:
  - /dev/video0:/dev/video0  # Update to match your device
```

### Permission Issues on Linux

```bash
# Add your user to the video group
sudo usermod -a -G video $USER

# Add your user to the docker group (if not already)
sudo usermod -a -G docker $USER

# Log out and back in for changes to take effect
```

### Performance Issues on Raspberry Pi

1. Reduce worker count to 2
2. Lower camera resolution (320x240)
3. Reduce FPS to 15-20
4. Ensure adequate power supply (official Raspberry Pi power adapter recommended)

## Architecture

The application uses:
- **Flask** - Web framework
- **OpenCV** - Video capture and processing
- **Gunicorn** - Production WSGI server
- **Bootstrap 5** - Modern responsive UI
- **Docker** - Containerized deployment

## File Structure

```
simple-webcam-recorder/
├── app/                    # Flask application
│   ├── __init__.py        # App factory
│   ├── routes.py          # Web routes
│   ├── camera.py          # Camera handling
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JS, and static files
├── recordings/            # Saved video files (mounted volume)
├── config.py              # Configuration
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── entrypoint.sh          # Container startup script
├── requirements.txt       # Python dependencies
└── wsgi.py               # WSGI entry point
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Built with Flask, OpenCV, and Bootstrap 5.
