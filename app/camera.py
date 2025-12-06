"""Camera service for webcam streaming and recording."""
import cv2
import threading
import datetime
import os
from typing import Optional


class Camera:
    """Handles webcam streaming and recording."""
    
    def __init__(self, config):
        """Initialize camera with configuration."""
        self.config = config
        self.camera = None
        self.is_recording = False
        self.video_writer = None
        self.lock = threading.Lock()
        self.frame = None
        self.recording_filename = None
        
    def initialize(self):
        """Initialize the camera."""
        if self.camera is None:
            self.camera = cv2.VideoCapture(self.config['CAMERA_INDEX'])
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['CAMERA_WIDTH'])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['CAMERA_HEIGHT'])
            self.camera.set(cv2.CAP_PROP_FPS, self.config['CAMERA_FPS'])
            
    def get_frame(self):
        """Get the current frame from the camera."""
        self.initialize()
        
        with self.lock:
            success, frame = self.camera.read()
            if success:
                self.frame = frame.copy()
                
                # If recording, write the frame
                if self.is_recording and self.video_writer is not None:
                    self.video_writer.write(frame)
                
                # Encode frame to JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    return buffer.tobytes()
        return None
    
    def generate_frames(self):
        """Generator function for streaming frames."""
        while True:
            frame = self.get_frame()
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
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
