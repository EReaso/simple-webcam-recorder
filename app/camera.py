"""Camera service for webcam streaming and recording."""
import cv2
import threading
import datetime
import os
import numpy as np
import time
from typing import Optional


class Camera:
    """Handles webcam streaming and recording."""
    
    # Error message constants
    FALLBACK_ERROR_MSG = "Camera Error\nUnable to display error details"
    CAMERA_NOT_INIT_MSG = "Camera Error\nCamera not initialized\nCheck device permissions and connections"
    CAMERA_READ_FAIL_MSG = "Camera Error\nFailed to read from camera\nCheck if device is in use or disconnected"
    UNKNOWN_ERROR_MSG = "Camera Error\nUnknown error occurred"
    
    # Cleanup thread check interval in seconds
    CLEANUP_CHECK_INTERVAL = 2
    # Cleanup thread join timeout in seconds
    CLEANUP_THREAD_JOIN_TIMEOUT = 3
    
    def __init__(self, config):
        """Initialize camera with configuration."""
        self.config = config
        self.camera = None
        self.is_recording = False
        self.video_writer = None
        self.lock = threading.Lock()
        self.frame = None
        self.recording_filename = None
        self.camera_error = None
        self.error_frame = None
        
        # Camera lifecycle management
        self.active_viewers = 0
        self.last_access_time = None
        # Support both dict-like Flask config and config objects
        if hasattr(config, 'get'):
            self.idle_timeout = config.get('CAMERA_IDLE_TIMEOUT', 10)
        else:
            self.idle_timeout = getattr(config, 'CAMERA_IDLE_TIMEOUT', 10)
        self.cleanup_thread = None
        self.cleanup_stop_event = threading.Event()
        self._start_cleanup_thread()
        
    def create_error_frame(self, message: str) -> Optional[bytes]:
        """Create an error frame with a message.
        
        Args:
            message: Error message to display. Use newlines to separate lines.
            
        Returns:
            JPEG-encoded image bytes, or None if encoding fails.
        """
        width = self.config['CAMERA_WIDTH']
        height = self.config['CAMERA_HEIGHT']
        
        # Create a dark gray background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (50, 50, 50)
        
        # Add error icon (red X)
        center_x, center_y = width // 2, height // 3
        size = min(width, height) // 6
        cv2.line(frame, (center_x - size, center_y - size), 
                (center_x + size, center_y + size), (0, 0, 255), 5)
        cv2.line(frame, (center_x + size, center_y - size), 
                (center_x - size, center_y + size), (0, 0, 255), 5)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        color = (255, 255, 255)
        
        # Split message into lines
        lines = message.split('\n')
        line_height = 30
        start_y = center_y + size + 40
        
        for i, line in enumerate(lines):
            text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
            text_x = (width - text_size[0]) // 2
            text_y = start_y + i * line_height
            # Ensure text stays within frame boundaries
            if text_y + 10 < height:  # Leave margin at bottom
                cv2.putText(frame, line, (text_x, text_y), font, font_scale, color, font_thickness)
        
        # Encode to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            return buffer.tobytes()
        return None
    
    def _get_error_frame_with_fallback(self, error_msg: str, cache: bool = True) -> Optional[bytes]:
        """Create an error frame with fallback handling.
        
        Args:
            error_msg: Primary error message to display.
            cache: Whether to cache the error frame.
            
        Returns:
            JPEG-encoded error frame bytes.
        """
        error_frame = self.create_error_frame(error_msg)
        if cache and error_frame is not None:
            self.error_frame = error_frame
        # If primary error frame creation failed, try fallback
        if error_frame is None:
            error_frame = self.create_error_frame(self.FALLBACK_ERROR_MSG)
        return error_frame
    
    def _start_cleanup_thread(self):
        """Start the background cleanup thread."""
        if self.cleanup_thread is None or not self.cleanup_thread.is_alive():
            self.cleanup_stop_event.clear()
            self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
            self.cleanup_thread.start()
    
    def _cleanup_worker(self):
        """Background worker that releases camera when idle."""
        while not self.cleanup_stop_event.is_set():
            time.sleep(self.CLEANUP_CHECK_INTERVAL)
            
            # Check if camera should be released due to inactivity
            # All checks done inside the lock to prevent race conditions
            with self.lock:
                if (self.camera is not None and 
                    not self.is_recording and 
                    self.active_viewers == 0 and
                    self.last_access_time is not None):
                    idle_time = time.time() - self.last_access_time
                    if idle_time > self.idle_timeout:
                        self.camera.release()
                        self.camera = None
                        self.last_access_time = None
        
    def initialize(self):
        """Initialize the camera."""
        if self.camera is None:
            try:
                self.camera = cv2.VideoCapture(self.config['CAMERA_INDEX'])
                
                # Check if camera opened successfully
                if not self.camera.isOpened():
                    self.camera_error = f"Camera Error\nCannot open camera at index {self.config['CAMERA_INDEX']}\nCheck device permissions and connections"
                    self.camera = None
                    return
                
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['CAMERA_WIDTH'])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['CAMERA_HEIGHT'])
                self.camera.set(cv2.CAP_PROP_FPS, self.config['CAMERA_FPS'])
                
                # Clear any previous errors
                self.camera_error = None
            except Exception as e:
                self.camera_error = f"Camera Error\n{str(e)}\nCheck device permissions and connections"
                self.camera = None
            
    def get_frame(self):
        """Get the current frame from the camera."""
        # Update last access time (protected by lock to prevent race conditions)
        with self.lock:
            self.last_access_time = time.time()
        
        self.initialize()
        
        # If camera initialization failed or camera has an error, return error frame
        if self.camera_error:
            if self.error_frame is None:
                self.error_frame = self.create_error_frame(self.camera_error)
            # If error frame creation failed, try to create a minimal fallback
            if self.error_frame is None:
                return self.create_error_frame(self.FALLBACK_ERROR_MSG)
            return self.error_frame
        
        # If camera is not available, return error frame
        if self.camera is None:
            if self.error_frame is None:
                self.error_frame = self.create_error_frame(self.CAMERA_NOT_INIT_MSG)
            # If error frame creation failed, try to create a minimal fallback
            if self.error_frame is None:
                return self.create_error_frame(self.FALLBACK_ERROR_MSG)
            return self.error_frame
        
        with self.lock:
            try:
                success, frame = self.camera.read()
                if success:
                    self.frame = frame.copy()
                    
                    # Clear error frame cache and error state since we got a successful read
                    self.error_frame = None
                    self.camera_error = None
                    
                    # If recording, write the frame
                    if self.is_recording and self.video_writer is not None:
                        self.video_writer.write(frame)
                    
                    # Encode frame to JPEG
                    ret, buffer = cv2.imencode('.jpg', frame)
                    if ret:
                        return buffer.tobytes()
                else:
                    # Camera read failed, create error frame with caching
                    return self._get_error_frame_with_fallback(self.CAMERA_READ_FAIL_MSG)
            except Exception as e:
                # Handle any other exceptions during frame reading
                error_msg = f"Camera Error\n{str(e)}\nCheck device permissions and connections"
                return self._get_error_frame_with_fallback(error_msg)
        
        # Fallback: return a basic error frame
        return self.create_error_frame(self.UNKNOWN_ERROR_MSG)
    
    def add_viewer(self):
        """Register a new viewer for the stream."""
        with self.lock:
            self.active_viewers += 1
    
    def remove_viewer(self):
        """Unregister a viewer from the stream."""
        with self.lock:
            self.active_viewers = max(0, self.active_viewers - 1)
    
    def generate_frames(self):
        """Generator function for streaming frames."""
        self.add_viewer()
        try:
            while True:
                frame = self.get_frame()
                if frame is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        finally:
            self.remove_viewer()
    
    def start_recording(self) -> Optional[str]:
        """Start recording video."""
        with self.lock:
            if self.is_recording:
                return None
            
            self.initialize()
            
            # Create recordings directory if it doesn't exist
            os.makedirs(self.config['RECORDINGS_DIR'], exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            self.recording_filename = f'recording_{timestamp}.{self.config["VIDEO_FORMAT"]}'
            filepath = os.path.join(self.config['RECORDINGS_DIR'], self.recording_filename)
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*self.config['VIDEO_CODEC'])
            self.video_writer = cv2.VideoWriter(
                filepath,
                fourcc,
                self.config['CAMERA_FPS'],
                (self.config['CAMERA_WIDTH'], self.config['CAMERA_HEIGHT'])
            )
            
            self.is_recording = True
            return self.recording_filename
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording video."""
        with self.lock:
            if not self.is_recording:
                return None
            
            self.is_recording = False
            
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None
            
            filename = self.recording_filename
            self.recording_filename = None
            return filename
    
    def get_recording_status(self) -> dict:
        """Get current recording status."""
        return {
            'is_recording': self.is_recording,
            'filename': self.recording_filename
        }
    
    def release(self):
        """Release camera resources."""
        # Stop the cleanup thread
        self.cleanup_stop_event.set()
        if self.cleanup_thread is not None:
            self.cleanup_thread.join(timeout=self.CLEANUP_THREAD_JOIN_TIMEOUT)
        
        with self.lock:
            if self.video_writer is not None:
                self.video_writer.release()
            if self.camera is not None:
                self.camera.release()
            self.camera = None


# Global camera instance
camera_instance = None


def get_camera(config):
    """Get or create the global camera instance."""
    global camera_instance
    if camera_instance is None:
        camera_instance = Camera(config)
    return camera_instance
