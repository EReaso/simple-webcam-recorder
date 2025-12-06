#!/usr/bin/env python3
"""Main entry point for the webcam recorder application."""
from app import app


if __name__ == '__main__':
    # Run the application
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
