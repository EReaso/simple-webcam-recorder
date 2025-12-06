# Simple Webcam Recorder

A configurable Flask web server for recording and streaming USB webcam video. Features a modern Bootstrap 5 web interface for easy control.

## Features

- 🎥 **Live webcam streaming** - Real-time video stream from USB camera
- 🔴 **Video recording** - Start/stop recording with one click
- 🎨 **Modern UI** - Clean Bootstrap 5 interface
- ⚙️ **Configurable** - Customize camera settings, resolution, FPS, and more
- 📁 **Recording management** - View list of recorded videos
- 🏭 **Application factory pattern** - Clean, scalable Flask architecture

## Requirements

- Python 3.9 or higher (or Docker)
- USB webcam
- Linux, macOS, or Windows

## Quick Start with Docker (Recommended)

The easiest way to run the application is using Docker:

1. Clone the repository:
```bash
git clone https://github.com/EReaso/simple-webcam-recorder.git
cd simple-webcam-recorder
```

2. Start with Docker Compose:
```bash
docker-compose up
```

3. Open your browser to `http://localhost:5000`

**Note:** On Linux, you may need to adjust the webcam device in `docker-compose.yml` if your camera is not at `/dev/video0`. Use `ls /dev/video*` to find your device.

## Installation (Without Docker)

1. Clone the repository:
```bash
git clone https://github.com/EReaso/simple-webcam-recorder.git
cd simple-webcam-recorder
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application can be configured using environment variables. Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

### Available Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `development` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` |
| `CAMERA_INDEX` | Camera device index (0 for default camera) | `0` |
| `CAMERA_WIDTH` | Video width in pixels | `640` |
| `CAMERA_HEIGHT` | Video height in pixels | `480` |
| `CAMERA_FPS` | Frames per second | `30` |
| `RECORDINGS_DIR` | Directory to save recordings | `./recordings` |
| `VIDEO_CODEC` | Video codec (mp4v, XVID, etc.) | `mp4v` |
| `VIDEO_FORMAT` | Output file format | `mp4` |
| `HOST` | Server host address | `0.0.0.0` |
| `PORT` | Server port | `5000` |
| `DEBUG` | Enable debug mode | `True` |
| `WORKERS` | Number of Gunicorn worker processes | `4` |

## Usage

### With Docker

```bash
# Start the application
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Without Docker

1. Start the server:
```bash
python run.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the web interface to:
   - View the live webcam stream
   - Start/stop video recording
   - View list of recorded videos

### Production Deployment

For production use, the application uses **Gunicorn** (a production-grade WSGI server) instead of Flask's development server:

```bash
# Production deployment with Gunicorn (default 4 workers)
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app

# Or configure workers via environment variable
WORKERS=8 ./entrypoint.sh
```

When using Docker (recommended), Gunicorn is used automatically and the number of workers can be configured via the `WORKERS` environment variable. The development server (`python run.py`) is only for local testing.

## Running as a System Service

To automatically start the webcam recorder on boot and run it as a background service, you can use **systemd** (Linux) to manage the application. This section provides step-by-step instructions for both Docker and native Python deployments.

### Option 1: Running as a Service with Docker (Recommended)

This method uses Docker Compose and is the simplest approach for production deployments.

#### 1. Install the application

```bash
# Clone the repository to a permanent location
sudo mkdir -p /opt/simple-webcam-recorder
cd /opt/simple-webcam-recorder
sudo git clone https://github.com/EReaso/simple-webcam-recorder.git .

# Configure environment variables (optional)
sudo cp .env.example .env
sudo nano .env  # Adjust settings as needed
```

#### 2. Create the systemd service file

```bash
sudo nano /etc/systemd/system/webcam-recorder.service
```

Add the following content (also available in `webcam-recorder-docker.service`):

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

#### 3. Enable and start the service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable webcam-recorder.service

# Start the service now
sudo systemctl start webcam-recorder.service

# Check service status
sudo systemctl status webcam-recorder.service
```

#### 4. Manage the service

```bash
# View logs
sudo journalctl -u webcam-recorder.service -f

# Or view Docker Compose logs
cd /opt/simple-webcam-recorder
sudo docker-compose logs -f

# Stop the service
sudo systemctl stop webcam-recorder.service

# Restart the service
sudo systemctl restart webcam-recorder.service

# Disable auto-start on boot
sudo systemctl disable webcam-recorder.service
```

### Option 2: Running as a Service with Native Python

This method runs the application directly with Python and Gunicorn without Docker.

#### 1. Install the application

```bash
# Clone the repository to a permanent location
sudo mkdir -p /opt/simple-webcam-recorder
cd /opt/simple-webcam-recorder
sudo git clone https://github.com/EReaso/simple-webcam-recorder.git .

# Set ownership to your user for installation
sudo chown -R $USER:$USER /opt/simple-webcam-recorder

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
nano .env  # Set FLASK_ENV=production and DEBUG=False

# Create recordings directory
mkdir -p recordings
```

#### 2. Create the systemd service file

```bash
sudo nano /etc/systemd/system/webcam-recorder.service
```

Add the following content (also available in `webcam-recorder.service`):

```ini
[Unit]
Description=Simple Webcam Recorder
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/simple-webcam-recorder
Environment="PATH=/opt/simple-webcam-recorder/venv/bin"
ExecStart=/opt/simple-webcam-recorder/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Note:** You may need to adjust the `User` directive based on your system. Common options:
- `www-data` (Debian/Ubuntu)
- `nginx` or `http` (some systems)
- Your username (for development/testing)

#### 3. Set up permissions

```bash
# Option A: Run as www-data user (recommended for production)
sudo chown -R www-data:www-data /opt/simple-webcam-recorder
sudo usermod -a -G video www-data  # Grant webcam access

# Option B: Run as your user (simpler for testing)
# Change User=www-data to User=$USER in the service file above
# Then keep current ownership
sudo usermod -a -G video $USER  # Grant webcam access
```

#### 4. Enable and start the service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable webcam-recorder.service

# Start the service now
sudo systemctl start webcam-recorder.service

# Check service status
sudo systemctl status webcam-recorder.service
```

#### 5. Manage the service

```bash
# View logs
sudo journalctl -u webcam-recorder.service -f

# Stop the service
sudo systemctl stop webcam-recorder.service

# Restart the service
sudo systemctl restart webcam-recorder.service

# Disable auto-start on boot
sudo systemctl disable webcam-recorder.service
```

### Service Configuration Tips

#### Adjusting Worker Count

For better performance, adjust the number of Gunicorn workers based on your CPU:

- **Recommended formula:** `(2 × CPU_cores) + 1`
- For a 4-core CPU: 9 workers
- For a 2-core CPU: 5 workers
- For Raspberry Pi: 2-3 workers (limited resources)

**Docker method:** Edit `docker-compose.yml` or set environment variable:
```yaml
environment:
  - WORKERS=9
```

**Native Python method:** Edit the service file:
```ini
ExecStart=/opt/simple-webcam-recorder/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 9 --timeout 120 wsgi:app
```

#### Changing the Port

**Docker method:** Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Change 8080 to your desired port
```

**Native Python method:** Edit the service file:
```ini
ExecStart=/opt/simple-webcam-recorder/venv/bin/gunicorn --bind 0.0.0.0:8080 --workers 4 --timeout 120 wsgi:app
```

### ARM/Raspberry Pi Deployment

Running as a service on ARM-based devices like Raspberry Pi requires some adjustments due to limited resources.

#### Docker Method (Recommended for Raspberry Pi)

1. **Use the standard Docker deployment** as described in Option 1 above, but adjust the worker count:

   Edit `docker-compose.yml` or create a `.env` file with:
   ```bash
   WORKERS=2
   ```

2. **Follow the Docker service setup** from Option 1 (steps 1-4)

#### Native Python Method for ARM/Raspberry Pi

For ARM devices, use `opencv-python-headless` instead of `opencv-python` for better compatibility:

1. **Install the application:**
   ```bash
   # Clone the repository to a permanent location
   sudo mkdir -p /opt/simple-webcam-recorder
   cd /opt/simple-webcam-recorder
   sudo git clone https://github.com/EReaso/simple-webcam-recorder.git .
   
   # Set ownership to your user for installation
   sudo chown -R $USER:$USER /opt/simple-webcam-recorder
   
   # Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install ARM-optimized dependencies
   pip install Flask==3.0.0
   pip install opencv-python-headless==4.8.1.78
   pip install numpy==1.26.2
   pip install gunicorn==23.0.0
   
   # Configure environment variables
   cp .env.example .env
   nano .env  # Set FLASK_ENV=production, DEBUG=False, and WORKERS=2
   
   # Create recordings directory
   mkdir -p recordings
   ```

2. **Create the systemd service file:**
   ```bash
   sudo nano /etc/systemd/system/webcam-recorder.service
   ```

   Use this ARM-optimized configuration:
   ```ini
   [Unit]
   Description=Simple Webcam Recorder (ARM)
   After=network.target
   
   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/opt/simple-webcam-recorder
   Environment="PATH=/opt/simple-webcam-recorder/venv/bin"
   ExecStart=/opt/simple-webcam-recorder/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 wsgi:app
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

   **Note:** Change `User=pi` to your Raspberry Pi username if different.

3. **Set up permissions:**
   ```bash
   # Keep ownership with your user (typically 'pi' on Raspberry Pi)
   sudo chown -R $USER:$USER /opt/simple-webcam-recorder
   sudo usermod -a -G video $USER  # Grant webcam access
   ```

4. **Enable and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable webcam-recorder.service
   sudo systemctl start webcam-recorder.service
   sudo systemctl status webcam-recorder.service
   ```

#### ARM/Raspberry Pi Performance Tips

- **Use 2 workers maximum** - Raspberry Pi has limited CPU and memory
- **Consider lowering resolution** - Set `CAMERA_WIDTH=320` and `CAMERA_HEIGHT=240` in `.env` for better performance
- **Monitor temperature** - Use `vcgencmd measure_temp` on Raspberry Pi to check temperature
- **Use headless OpenCV** - `opencv-python-headless` uses less memory than standard `opencv-python`

### Troubleshooting Service Issues

#### Service fails to start

1. **Check the service status and logs:**
   ```bash
   sudo systemctl status webcam-recorder.service
   sudo journalctl -u webcam-recorder.service -n 50
   ```

2. **Verify file permissions:**
   ```bash
   ls -la /opt/simple-webcam-recorder
   # Ensure the service user has read/write access
   ```

3. **Test manually before enabling the service:**
   ```bash
   # For Docker
   cd /opt/simple-webcam-recorder
   docker-compose up
   
   # For native Python
   cd /opt/simple-webcam-recorder
   source venv/bin/activate
   gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
   ```

#### Camera not accessible

1. **Ensure the service user is in the video group:**
   ```bash
   sudo usermod -a -G video www-data  # Or your service user
   ```

2. **Check camera device permissions:**
   ```bash
   ls -la /dev/video*
   # Should show rw-rw---- or similar with video group
   ```

3. **For Docker, verify device mapping** in `docker-compose.yml`:
   ```yaml
   devices:
     - /dev/video0:/dev/video0
   ```

#### Port already in use

1. **Find what's using the port:**
   ```bash
   sudo lsof -i :5000
   ```

2. **Stop the conflicting service or change the port** (see "Changing the Port" above)

#### Recordings directory permission denied

```bash
# Ensure the service user can write to recordings directory
sudo chown -R www-data:www-data /opt/simple-webcam-recorder/recordings
sudo chmod -R 755 /opt/simple-webcam-recorder/recordings
```

## Project Structure

```
simple-webcam-recorder/
├── app/
│   ├── __init__.py                 # Flask application initialization
│   ├── routes.py                   # Application routes (using blueprints)
│   ├── camera.py                   # Camera service for streaming/recording
│   └── templates/
│       └── index.html              # Main web interface
├── recordings/                     # Directory for saved videos
├── config.py                       # Configuration settings
├── run.py                          # Development server entry point
├── wsgi.py                         # Production WSGI entry point
├── entrypoint.sh                   # Production startup script
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image configuration
├── docker-compose.yml              # Docker Compose setup
├── webcam-recorder.service         # systemd service file (native Python)
├── webcam-recorder-docker.service  # systemd service file (Docker)
├── webcam-recorder-arm.service     # systemd service file (ARM/Raspberry Pi)
├── .dockerignore                   # Docker ignore rules
├── .env.example                    # Example environment configuration
└── README.md                       # This file
```

## API Endpoints

The application provides the following REST API endpoints:

- `GET /` - Main web interface
- `GET /video_feed` - MJPEG video stream
- `POST /api/recording/start` - Start recording
- `POST /api/recording/stop` - Stop recording
- `GET /api/recording/status` - Get recording status
- `GET /api/recordings` - List all recordings

## Architecture

The application uses Flask with blueprints for clean code organization:
- Routes are defined in `app/routes.py` using Flask blueprints
- Camera service provides thread-safe video capture and recording
- Configuration managed through environment variables

## Troubleshooting

### Docker-specific issues

#### Camera not accessible in Docker
- On Linux, ensure the webcam device is mapped correctly in `docker-compose.yml`
- Check available devices: `ls /dev/video*`
- You may need to run Docker with privileged mode for some systems:
  ```yaml
  privileged: true
  ```

#### Permission denied for webcam in Docker
- On Linux, add your user to the `video` group:
  ```bash
  sudo usermod -a -G video $USER
  ```
- Run Docker containers with the video group:
  ```yaml
  group_add:
    - video
  ```

### General troubleshooting

### Camera not found
- Ensure your webcam is connected
- Try changing `CAMERA_INDEX` (try 0, 1, 2, etc.)
- Check camera permissions on your system

### Permission denied
- On Linux, you may need to add your user to the `video` group:
```bash
sudo usermod -a -G video $USER
```

### Poor video quality
- Increase `CAMERA_WIDTH` and `CAMERA_HEIGHT`
- Adjust `CAMERA_FPS` based on your camera capabilities
- Try different `VIDEO_CODEC` values (XVID, H264, etc.)

## License

See LICENSE file for details. 
