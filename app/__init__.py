"""Flask application factory."""
from flask import Flask, render_template, Response, jsonify, request
from config import config
from app.camera import get_camera
import os


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Get camera instance
    camera = get_camera(app.config)
    
    @app.route('/')
    def index():
        """Render the main page."""
        return render_template('index.html')
    
    @app.route('/video_feed')
    def video_feed():
        """Video streaming route."""
        return Response(
            camera.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    
    @app.route('/api/recording/start', methods=['POST'])
    def start_recording():
        """Start recording endpoint."""
        filename = camera.start_recording()
        if filename:
            return jsonify({
                'status': 'success',
                'message': 'Recording started',
                'filename': filename
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Recording already in progress'
            }), 400
    
    @app.route('/api/recording/stop', methods=['POST'])
    def stop_recording():
        """Stop recording endpoint."""
        filename = camera.stop_recording()
        if filename:
            return jsonify({
                'status': 'success',
                'message': 'Recording stopped',
                'filename': filename
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No recording in progress'
            }), 400
    
    @app.route('/api/recording/status', methods=['GET'])
    def recording_status():
        """Get recording status endpoint."""
        status = camera.get_recording_status()
        return jsonify(status)
    
    @app.route('/api/recordings', methods=['GET'])
    def list_recordings():
        """List all recordings."""
        recordings_dir = app.config['RECORDINGS_DIR']
        if not os.path.exists(recordings_dir):
            return jsonify({'recordings': []})
        
        files = []
        for filename in os.listdir(recordings_dir):
            if filename.endswith(('.mp4', '.avi', '.mov')):
                filepath = os.path.join(recordings_dir, filename)
                files.append({
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'created': os.path.getctime(filepath)
                })
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'recordings': files})
    
    @app.teardown_appcontext
    def cleanup(error=None):
        """Cleanup resources on app shutdown."""
        # Camera cleanup is handled by the global instance
        pass
    
    return app
