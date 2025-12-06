"""Flask application routes."""
from flask import Blueprint, render_template, Response, jsonify, current_app
import os

# Create blueprint for main routes
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@main_bp.route('/video_feed')
def video_feed():
    """Video streaming route."""
    camera = current_app.config['camera']
    return Response(
        camera.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@main_bp.route('/api/recording/start', methods=['POST'])
def start_recording():
    """Start recording endpoint."""
    camera = current_app.config['camera']
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


@main_bp.route('/api/recording/stop', methods=['POST'])
def stop_recording():
    """Stop recording endpoint."""
    camera = current_app.config['camera']
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


@main_bp.route('/api/recording/status', methods=['GET'])
def recording_status():
    """Get recording status endpoint."""
    camera = current_app.config['camera']
    status = camera.get_recording_status()
    return jsonify(status)


@main_bp.route('/api/recordings', methods=['GET'])
def list_recordings():
    """List all recordings."""
    recordings_dir = current_app.config['RECORDINGS_DIR']
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
