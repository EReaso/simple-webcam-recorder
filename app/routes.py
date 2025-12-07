"""Flask application routes."""
from flask import Blueprint, render_template, Response, jsonify, current_app, send_from_directory
import os
import logging

# Create blueprint for main routes
main_bp = Blueprint('main', __name__)

# Set up logging
logger = logging.getLogger(__name__)


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


@main_bp.route('/api/stream/rtsp/start', methods=['POST'])
def start_rtsp_stream():
    """Start RTSP streaming endpoint."""
    stream_manager = current_app.config.get('stream_manager')
    if not stream_manager:
        return jsonify({
            'status': 'error',
            'message': 'RTSP streaming is not enabled'
        }), 400
    
    camera = current_app.config['camera']
    if stream_manager.start_streaming(camera):
        return jsonify({
            'status': 'success',
            'message': 'RTSP streaming started',
            'rtsp_url': stream_manager.get_rtsp_url()
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to start RTSP streaming'
        }), 500


@main_bp.route('/api/stream/rtsp/stop', methods=['POST'])
def stop_rtsp_stream():
    """Stop RTSP streaming endpoint."""
    stream_manager = current_app.config.get('stream_manager')
    if not stream_manager:
        return jsonify({
            'status': 'error',
            'message': 'RTSP streaming is not enabled'
        }), 400
    
    stream_manager.stop_streaming()
    return jsonify({
        'status': 'success',
        'message': 'RTSP streaming stopped'
    })


@main_bp.route('/api/stream/rtsp/status', methods=['GET'])
def rtsp_stream_status():
    """Get RTSP streaming status endpoint."""
    stream_manager = current_app.config.get('stream_manager')
    if not stream_manager:
        return jsonify({
            'enabled': False,
            'active': False
        })
    
    return jsonify({
        'enabled': True,
        'active': stream_manager.is_active(),
        'rtsp_url': stream_manager.get_rtsp_url() if stream_manager.is_active() else None
    })


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
    if status['is_recording'] and status['filename']:
        # Normalize both filenames for comparison
        try:
            status_filepath = os.path.join(recordings_dir, status['filename'])
            if os.path.exists(filepath) and os.path.exists(status_filepath):
                if os.path.samefile(filepath, status_filepath):
                    return jsonify({
                        'status': 'error',
                        'message': 'Cannot delete file currently being recorded'
                    }), 400
            elif status['filename'] == filename:
                # Fallback to string comparison if files don't exist yet
                return jsonify({
                    'status': 'error',
                    'message': 'Cannot delete file currently being recorded'
                }), 400
        except (OSError, ValueError):
            # If samefile fails, use string comparison
            if status['filename'] == filename:
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
        # Log the actual error for debugging (sanitize filename for log injection prevention)
        safe_filename = filename.replace('\n', '').replace('\r', '')
        logger.error(f'Failed to delete recording {safe_filename}: {str(e)}')
        # Return generic error message to client
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete file'
        }), 500
