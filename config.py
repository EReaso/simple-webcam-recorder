"""Configuration settings for the webcam recorder application."""
import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Camera settings
    CAMERA_INDEX = int(os.environ.get('CAMERA_INDEX', 0))
    CAMERA_WIDTH = int(os.environ.get('CAMERA_WIDTH', 640))
    CAMERA_HEIGHT = int(os.environ.get('CAMERA_HEIGHT', 480))
    CAMERA_FPS = int(os.environ.get('CAMERA_FPS', 30))
    
    # Recording settings
    RECORDINGS_DIR = os.environ.get('RECORDINGS_DIR') or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'recordings'
    )
    VIDEO_CODEC = os.environ.get('VIDEO_CODEC', 'mp4v')
    VIDEO_FORMAT = os.environ.get('VIDEO_FORMAT', 'mp4')
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    WORKERS = int(os.environ.get('WORKERS', 4))  # Number of Gunicorn workers


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
