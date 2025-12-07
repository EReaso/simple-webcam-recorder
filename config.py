"""Configuration settings for the webcam recorder application."""
import os
import secrets


class Config:
    """Base configuration."""
    # Generate a random secret key on startup if not provided
    # This ensures each instance has a unique secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Camera settings
    CAMERA_INDEX = int(os.environ.get('CAMERA_INDEX', 0))
    CAMERA_WIDTH = int(os.environ.get('CAMERA_WIDTH', 640))
    CAMERA_HEIGHT = int(os.environ.get('CAMERA_HEIGHT', 480))
    CAMERA_FPS = int(os.environ.get('CAMERA_FPS', 30))
    CAMERA_IDLE_TIMEOUT = int(os.environ.get('CAMERA_IDLE_TIMEOUT', 10))  # Seconds before releasing camera when idle
    
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
    
    # RTSP streaming settings
    RTSP_ENABLED = os.environ.get('RTSP_ENABLED', 'True').lower() == 'true'
    RTSP_OUTPUT_URL = os.environ.get('RTSP_OUTPUT_URL', 'rtsp://mediamtx:8554/live')
    RTSP_PUBLIC_HOST = os.environ.get('RTSP_PUBLIC_HOST', 'localhost')
    RTSP_PUBLIC_PORT = os.environ.get('RTSP_PUBLIC_PORT', '8554')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig  # Default to production for deployments
}
