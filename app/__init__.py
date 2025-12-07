"""Flask application initialization."""
from flask import Flask
from config import config
from app.camera import get_camera
from app.stream_manager import get_stream_manager
from app.routes import main_bp
import os


# Initialize Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Initialize camera and store in app config for access by routes
camera = get_camera(app.config)
app.config['camera'] = camera

# Initialize stream manager if RTSP is enabled
if app.config.get('RTSP_ENABLED', True):
    stream_manager = get_stream_manager(app.config)
    app.config['stream_manager'] = stream_manager
    # Link camera with stream manager
    camera.set_stream_manager(stream_manager)
else:
    app.config['stream_manager'] = None

# Register blueprints
app.register_blueprint(main_bp)


@app.teardown_appcontext
def cleanup(error=None):
    """Cleanup resources on app shutdown."""
    # Stop RTSP streaming if active
    if app.config.get('stream_manager'):
        app.config['stream_manager'].stop_streaming()
    # Camera cleanup is handled by the global instance
    pass

