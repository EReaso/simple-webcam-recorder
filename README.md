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

- Python 3.7 or higher
- USB webcam
- Linux, macOS, or Windows

## Installation

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

## Usage

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

## Project Structure

```
simple-webcam-recorder/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── camera.py            # Camera service for streaming/recording
│   └── templates/
│       └── index.html       # Main web interface
├── recordings/              # Directory for saved videos
├── config.py                # Configuration settings
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment configuration
└── README.md               # This file
```

## API Endpoints

The application provides the following REST API endpoints:

- `GET /` - Main web interface
- `GET /video_feed` - MJPEG video stream
- `POST /api/recording/start` - Start recording
- `POST /api/recording/stop` - Stop recording
- `GET /api/recording/status` - Get recording status
- `GET /api/recordings` - List all recordings

## Development

The application uses the Flask application factory pattern for better modularity and testing:

```python
from app import create_app

app = create_app('development')
```

## Troubleshooting

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
