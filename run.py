#!/usr/bin/env python3
"""Main entry point for the webcam recorder application."""
import os
from app import create_app


if __name__ == '__main__':
    # Get configuration from environment or use default
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create the application
    app = create_app(config_name)
    
    # Run the application
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
