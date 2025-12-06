"""Flask application initialization."""
from flask import Flask
from config import config
from app.camera import get_camera
from app.routes import main_bp, init_camera
import os


# Initialize Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Initialize camera
camera = get_camera(app.config)
init_camera(camera)

# Register blueprints
app.register_blueprint(main_bp)


@app.teardown_appcontext
def cleanup(error=None):
    """Cleanup resources on app shutdown."""
    # Camera cleanup is handled by the global instance
    pass

