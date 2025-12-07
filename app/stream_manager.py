"""Stream manager for handling MJPEG and RTSP streaming via FFMPEG."""
import subprocess
import threading
import time
import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class StreamManager:
    """Manages streaming to RTSP server using FFMPEG."""
    
    def __init__(self, config):
        """Initialize stream manager."""
        self.config = config
        self.ffmpeg_process = None
        self.is_streaming = False
        self.lock = threading.Lock()
        self.stream_thread = None
        self.stop_event = threading.Event()
        
        # RTSP server settings - handle both dict and object config
        self.rtsp_url = self._get_config('RTSP_OUTPUT_URL', 'rtsp://mediamtx:8554/live')
        self.width = self._get_config('CAMERA_WIDTH', 640)
        self.height = self._get_config('CAMERA_HEIGHT', 480)
        self.fps = self._get_config('CAMERA_FPS', 30)
    
    def _get_config(self, key, default=None):
        """Get configuration value, handling both dict and object configs.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if hasattr(self.config, 'get'):
            return self.config.get(key, default)
        else:
            return getattr(self.config, key, default)
        
    def start_streaming(self, camera):
        """Start streaming to RTSP server.
        
        Args:
            camera: Camera instance to stream from
        """
        with self.lock:
            if self.is_streaming:
                logger.info("Streaming already active")
                return True
            
            try:
                # Build FFMPEG command to receive raw video and stream to RTSP
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-y',  # Overwrite output
                    '-f', 'rawvideo',
                    '-vcodec', 'rawvideo',
                    '-pix_fmt', 'bgr24',
                    '-s', f'{self.width}x{self.height}',
                    '-r', str(self.fps),
                    '-i', '-',  # Read from stdin
                    '-c:v', 'libx264',
                    '-preset', 'ultrafast',
                    '-tune', 'zerolatency',
                    '-f', 'rtsp',
                    self.rtsp_url
                ]
                
                logger.info(f"Starting FFMPEG stream to {self.rtsp_url}")
                self.ffmpeg_process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=10**8
                )
                
                self.is_streaming = True
                self.stop_event.clear()
                
                # Start thread to feed frames to FFMPEG
                self.stream_thread = threading.Thread(
                    target=self._stream_worker,
                    args=(camera,),
                    daemon=True
                )
                self.stream_thread.start()
                
                logger.info("RTSP streaming started successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to start RTSP streaming: {e}")
                self.is_streaming = False
                if self.ffmpeg_process:
                    self.ffmpeg_process.terminate()
                    self.ffmpeg_process = None
                return False
    
    def _stream_worker(self, camera):
        """Worker thread that feeds frames to FFMPEG.
        
        Args:
            camera: Camera instance to get frames from
        """
        frame_interval = 1.0 / self.fps
        
        while not self.stop_event.is_set() and self.is_streaming:
            try:
                # Get frame from camera (this is the raw numpy array)
                with camera.lock:
                    if camera.camera is None:
                        camera.initialize()
                    
                    if camera.camera is not None:
                        success, frame = camera.camera.read()
                        if success and frame is not None:
                            # Write raw frame to FFMPEG stdin
                            try:
                                self.ffmpeg_process.stdin.write(frame.tobytes())
                            except (BrokenPipeError, IOError) as e:
                                logger.error(f"FFMPEG pipe error: {e}")
                                break
                        else:
                            # Camera read failed, wait a bit
                            time.sleep(0.1)
                    else:
                        # Camera not initialized, wait
                        time.sleep(0.1)
                
                # Sleep to maintain frame rate
                time.sleep(frame_interval)
                
            except Exception as e:
                logger.error(f"Error in stream worker: {e}")
                time.sleep(0.1)
        
        logger.info("Stream worker stopped")
    
    def stop_streaming(self):
        """Stop streaming to RTSP server."""
        with self.lock:
            if not self.is_streaming:
                return
            
            logger.info("Stopping RTSP streaming")
            self.is_streaming = False
            self.stop_event.set()
            
            # Wait for stream thread to finish
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=2)
            
            # Terminate FFMPEG process
            if self.ffmpeg_process:
                try:
                    self.ffmpeg_process.stdin.close()
                    self.ffmpeg_process.terminate()
                    self.ffmpeg_process.wait(timeout=2)
                except Exception as e:
                    logger.error(f"Error stopping FFMPEG: {e}")
                    try:
                        self.ffmpeg_process.kill()
                    except Exception:
                        # FFMPEG process may already be terminated
                        pass
                finally:
                    self.ffmpeg_process = None
            
            logger.info("RTSP streaming stopped")
    
    def is_active(self):
        """Check if streaming is currently active."""
        return self.is_streaming
    
    def get_rtsp_url(self):
        """Get the RTSP URL for clients."""
        # Return public URL (replace mediamtx hostname with actual host)
        host = self._get_config('RTSP_PUBLIC_HOST', 'localhost')
        port = self._get_config('RTSP_PUBLIC_PORT', '8554')
        return f'rtsp://{host}:{port}/live'


# Global stream manager instance
stream_manager_instance = None


def get_stream_manager(config):
    """Get or create the global stream manager instance."""
    global stream_manager_instance
    if stream_manager_instance is None:
        stream_manager_instance = StreamManager(config)
    return stream_manager_instance
