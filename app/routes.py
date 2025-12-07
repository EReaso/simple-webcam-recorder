"""Flask application routes."""
from flask import Blueprint, render_template, Response, jsonify, current_app, send_from_directory
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


@main_bp.route('/api/recordings/<filename>', methods=['GET'])
def download_recording(filename):
    """Download a specific recording."""
    recordings_dir = current_app.config['RECORDINGS_DIR']
    
    # Security check: prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({
            'status': 'error',
            'message': 'Invalid filename'
        }), 400
    
    # Check if file exists and is a valid video file
    if not filename.endswith(('.mp4', '.avi', '.mov')):
        return jsonify({
            'status': 'error',
            'message': 'Invalid file type'
        }), 400
    
    filepath = os.path.join(recordings_dir, filename)
    if not os.path.exists(filepath):
        return jsonify({
            'status': 'error',
            'message': 'File not found'
        }), 404
    
    return send_from_directory(recordings_dir, filename, as_attachment=True)


@main_bp.route('/api/recordings/<filename>', methods=['DELETE'])
def delete_recording(filename):
    """Delete a specific recording."""
    recordings_dir = current_app.config['RECORDINGS_DIR']
    
    # Security check: prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({
            'status': 'error',
            'message': 'Invalid filename'
        }), 400
    
    # Check if file is a valid video file
    if not filename.endswith(('.mp4', '.avi', '.mov')):
        return jsonify({
            'status': 'error',
            'message': 'Invalid file type'
        }), 400
    
    filepath = os.path.join(recordings_dir, filename)
    if not os.path.exists(filepath):
        return jsonify({
            'status': 'error',
            'message': 'File not found'
        }), 404
    
    # Check if file is currently being recorded
    camera = current_app.config['camera']
    status = camera.get_recording_status()
    if status['is_recording'] and status['filename'] == filename:
        return jsonify({
            'status': 'error',
            'message': 'Cannot delete file currently being recorded'
        }), 400
    
    try:
        os.remove(filepath)
        return jsonify({
            'status': 'success',
            'message': 'Recording deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete file: {str(e)}'
        }), 500
