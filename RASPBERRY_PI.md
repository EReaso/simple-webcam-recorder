# Raspberry Pi Setup Guide

This guide explains how to run the Simple Webcam Recorder on Raspberry Pi (ARM architecture).

## Supported Devices

- Raspberry Pi 3 (Model B/B+)
- Raspberry Pi 4 (all variants)
- Raspberry Pi 5
- Other ARM-based single-board computers running Linux

## Prerequisites

- Raspberry Pi running Raspberry Pi OS (64-bit or 32-bit)
- USB webcam or Raspberry Pi Camera Module (with appropriate configuration)
- Docker and Docker Compose installed
- At least 1GB of free RAM
- 1GB of free disk space

## Installation

### Option 1: Docker (Recommended for Raspberry Pi)

Docker provides the easiest setup on Raspberry Pi with all dependencies pre-configured.

#### 1. Install Docker

If you haven't installed Docker yet:

```bash
# Update package list
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to the docker group (to run without sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install -y docker-compose

# Log out and back in for group changes to take effect
```

#### 2. Clone the Repository

```bash
git clone https://github.com/EReaso/simple-webcam-recorder.git
cd simple-webcam-recorder
```

#### 3. Start the Application

Use the ARM-optimized Docker Compose configuration:

```bash
# Start the application using ARM configuration
docker-compose -f docker-compose.arm.yml up -d

# View logs
docker-compose -f docker-compose.arm.yml logs -f
```

#### 4. Access the Web Interface

Open a web browser on your Raspberry Pi or another device on the same network:

```
http://[raspberry-pi-ip]:5000
```

To find your Raspberry Pi's IP address:
```bash
hostname -I
```

### Option 2: Native Installation (Without Docker)

For direct installation on Raspberry Pi OS:

#### 1. Install System Dependencies

```bash
# Update package list
sudo apt-get update

# Install Python and development tools
sudo apt-get install -y python3 python3-pip python3-venv

# Install OpenCV system dependencies
sudo apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgl1 \
    libgstreamer1.0-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev
```

#### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/EReaso/simple-webcam-recorder.git
cd simple-webcam-recorder

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install ARM-optimized dependencies
pip install -r requirements.arm.txt
```

#### 3. Configure Camera

For Raspberry Pi Camera Module (not USB):

```bash
# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options -> Camera -> Enable

# Reboot
sudo reboot
```

For USB webcam, no additional configuration needed.

#### 4. Run the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python run.py
```

Access at `http://localhost:5000` or `http://[raspberry-pi-ip]:5000`

## Configuration for Raspberry Pi

### Performance Tuning

Create a `.env` file with optimized settings for Raspberry Pi:

```bash
cp .env.example .env
```

Edit `.env` with recommended Raspberry Pi settings:

```env
# Reduce workers for limited resources
WORKERS=2

# Lower resolution for better performance
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_FPS=30

# Use efficient codec
VIDEO_CODEC=mp4v
VIDEO_FORMAT=mp4

# Production settings
FLASK_ENV=production
DEBUG=False
```

### Camera Selection

If you have multiple cameras or using Raspberry Pi Camera Module:

```bash
# List available video devices
ls -la /dev/video*

# Test camera (install v4l-utils if needed)
sudo apt-get install v4l-utils
v4l2-ctl --list-devices
```

Update `CAMERA_INDEX` in your `.env` file or docker-compose configuration accordingly.

### Raspberry Pi Camera Module

To use the Raspberry Pi Camera Module with Docker:

1. Enable legacy camera stack (required for Docker):
```bash
sudo raspi-config
# Navigate to: Interface Options -> Legacy Camera -> Enable
sudo reboot
```

2. Verify camera device:
```bash
ls -la /dev/video*
# Should show /dev/video0
```

3. Update device mapping in `docker-compose.arm.yml` if needed.

## Troubleshooting

### Camera Not Detected

**For USB Webcam:**
```bash
# Check if camera is recognized
lsusb

# Check video devices
ls -la /dev/video*

# Test camera
v4l2-ctl --list-formats-ext -d /dev/video0
```

**For Raspberry Pi Camera Module:**
```bash
# Verify camera is enabled
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test camera
raspistill -o test.jpg
```

### Performance Issues

If the application is slow on Raspberry Pi:

1. **Reduce resolution** in `.env`:
   ```env
   CAMERA_WIDTH=320
   CAMERA_HEIGHT=240
   CAMERA_FPS=15
   ```

2. **Reduce workers** (especially on Pi 3):
   ```env
   WORKERS=1
   ```

3. **Enable GPU acceleration** (if available):
   ```bash
   # Add to /boot/config.txt
   gpu_mem=128
   ```

4. **Close other applications** to free up RAM

5. **Use a cooling solution** to prevent thermal throttling

### Permission Denied

```bash
# Add user to video group
sudo usermod -aG video $USER

# For Docker
sudo usermod -aG docker $USER

# Log out and back in
```

### Out of Memory

For Raspberry Pi with limited RAM:

1. **Increase swap space**:
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Set CONF_SWAPSIZE=1024
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

2. **Reduce workers** to 1 in configuration

3. **Lower resolution** and FPS

### Docker Build Fails

If Docker build fails due to memory:

```bash
# Build with limited memory
docker-compose -f docker-compose.arm.yml build --memory 1g

# Or build without cache
docker-compose -f docker-compose.arm.yml build --no-cache --memory 1g
```

## Performance Tips

### Raspberry Pi 3
- Use `WORKERS=1` or `WORKERS=2`
- Resolution: 320x240 or 640x480
- FPS: 15-20
- Consider using lightweight OS (Raspberry Pi OS Lite)

### Raspberry Pi 4 (4GB/8GB)
- Use `WORKERS=2`
- Resolution: 640x480 or 1280x720
- FPS: 30
- Can handle multiple concurrent streams

### Raspberry Pi 5
- Use `WORKERS=2` or `WORKERS=4`
- Resolution: 1280x720 or 1920x1080
- FPS: 30
- Best performance with USB 3.0 cameras

## Network Access

To access from other devices on your network:

1. **Find your Raspberry Pi's IP:**
   ```bash
   hostname -I
   ```

2. **Access from browser:**
   ```
   http://192.168.1.XXX:5000
   ```

3. **Set static IP** (optional, recommended):
   - Edit `/etc/dhcpcd.conf` to set static IP
   - Or configure through your router's DHCP settings

## Starting on Boot

### With Docker (Recommended)

Docker containers with `restart: unless-stopped` will automatically start on boot.

### Without Docker

Create a systemd service:

```bash
# Create service file
sudo nano /etc/systemd/system/webcam-recorder.service
```

Add the following content (adjust paths):

```ini
[Unit]
Description=Simple Webcam Recorder
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/simple-webcam-recorder
Environment="PATH=/home/pi/simple-webcam-recorder/venv/bin"
ExecStart=/home/pi/simple-webcam-recorder/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable webcam-recorder
sudo systemctl start webcam-recorder
sudo systemctl status webcam-recorder
```

## Security Considerations

Since Raspberry Pi may be exposed on your network:

1. **Change default passwords** on your Raspberry Pi
2. **Use firewall** to restrict access:
   ```bash
   sudo apt-get install ufw
   sudo ufw allow 5000/tcp
   sudo ufw enable
   ```
3. **Consider adding authentication** to the application
4. **Use HTTPS** with a reverse proxy (nginx)
5. **Keep system updated**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

## Additional Resources

- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)
- [Raspberry Pi Camera Setup](https://www.raspberrypi.org/documentation/accessories/camera.html)
- [Docker on Raspberry Pi](https://docs.docker.com/engine/install/debian/)

## Support

For Raspberry Pi specific issues:
1. Check this guide's troubleshooting section
2. Review the main [README.md](README.md) for general issues
3. Check [DOCKER.md](DOCKER.md) for Docker-related problems
4. Open an issue on GitHub with details about your Raspberry Pi model and OS version
