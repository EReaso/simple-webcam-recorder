# Streaming Options

This application provides webcam streaming via both MJPEG (Motion JPEG) over HTTP and RTSP (Real Time Streaming Protocol).

## Built-in Streaming Protocols

### MJPEG Stream (HTTP)

The default streaming method is MJPEG over HTTP at the `/video_feed` endpoint:

- **URL**: `http://localhost:5000/video_feed`
- **Protocol**: HTTP multipart/x-mixed-replace
- **Format**: JPEG frames
- **Compatibility**: All modern browsers, VLC, ffmpeg
- **Use Case**: Web browser viewing, single viewer or small number of viewers

### RTSP Stream

RTSP streaming is provided via MediaMTX server and supports multiple concurrent viewers:

- **URL**: `rtsp://localhost:8554/live`
- **Protocol**: RTSP (Real Time Streaming Protocol)
- **Format**: H.264 video
- **Compatibility**: VLC, ffmpeg, most media players, security camera software
- **Use Case**: Multiple viewers, external applications, low latency streaming

## Accessing the Streams

### Web Browser (MJPEG)
Simply navigate to `http://localhost:5000` to view the stream in the web interface.

### RTSP Stream via VLC
1. Open VLC
2. Go to Media → Open Network Stream
3. Enter: `rtsp://localhost:8554/live`
4. Click Play

### RTSP Stream via ffmpeg
```bash
# Play the stream
ffplay rtsp://localhost:8554/live

# Save the stream to a file
ffmpeg -i rtsp://localhost:8554/live -c copy output.mp4
```

### RTSP Stream via curl (MJPEG endpoint)
```bash
# Save a single frame from MJPEG stream
curl http://localhost:5000/video_feed --output frame.jpg --max-time 1
```

## Managing RTSP Streaming

The RTSP stream can be controlled via the API:

### Start RTSP Stream
```bash
curl -X POST http://localhost:5000/api/stream/rtsp/start
```

Response:
```json
{
  "status": "success",
  "message": "RTSP streaming started",
  "rtsp_url": "rtsp://localhost:8554/live"
}
```

### Stop RTSP Stream
```bash
curl -X POST http://localhost:5000/api/stream/rtsp/stop
```

### Check RTSP Stream Status
```bash
curl http://localhost:5000/api/stream/rtsp/status
```

Response:
```json
{
  "enabled": true,
  "active": true,
  "rtsp_url": "rtsp://localhost:8554/live"
}
```

## Multi-Viewer Support

### MJPEG (HTTP)
- The MJPEG stream supports multiple concurrent viewers
- Each viewer receives frames from the same camera instance
- Camera is shared efficiently between viewers
- Automatic camera lifecycle management ensures the camera is only active when needed

### RTSP
- Better for multiple viewers (10+ concurrent streams)
- Lower bandwidth per viewer (H.264 compression)
- Offloads streaming work to MediaMTX server
- Can be accessed by external applications simultaneously

## Camera Resource Management

The application features intelligent camera lifecycle management:

- **Automatic Release**: Camera is released after 10 seconds when no viewers are watching and not recording (configurable via `CAMERA_IDLE_TIMEOUT`)
- **Viewer Tracking**: Each MJPEG stream viewer is tracked, keeping the camera active as long as someone is watching
- **RTSP Protection**: During RTSP streaming, the camera stays active
- **Recording Protection**: During recording, the camera stays active even with no viewers
- **On-Demand Access**: Camera is only initialized when actually needed

This ensures:
- ✅ Camera is not locked unnecessarily
- ✅ Other applications can access the camera when not in use
- ✅ Multiple viewers can watch simultaneously without errors
- ✅ Page reloads don't cause camera errors

## Configuration

### Enable/Disable RTSP

Edit `docker-compose.yml`:

```yaml
environment:
  - RTSP_ENABLED=true  # Set to false to disable RTSP streaming
```

### Change RTSP Server Settings

The RTSP server (MediaMTX) can be configured via environment variables:

```yaml
mediamtx:
  environment:
    - MTX_RTSPADDRESS=:8554  # RTSP port
```

### External Access

To allow external access to RTSP streams, update the public host in `docker-compose.yml`:

```yaml
environment:
  - RTSP_PUBLIC_HOST=192.168.1.100  # Your server's IP address
  - RTSP_PUBLIC_PORT=8554
```

Then use: `rtsp://192.168.1.100:8554/live`

## Performance Considerations

### MJPEG
- **Pros**: Simple, low latency, direct browser support
- **Cons**: Higher bandwidth usage, less efficient compression
- **Best for**: Single viewer, web browser viewing, low viewer count

### RTSP
- **Pros**: Efficient H.264 compression, multiple viewers, standard protocol
- **Cons**: Slight encoding latency, requires external player for viewing
- **Best for**: Multiple viewers (10+), external applications, long-running streams

### Bandwidth Usage Comparison
- MJPEG: ~5-15 Mbps per viewer (depending on resolution and FPS)
- RTSP (H.264): ~1-3 Mbps per viewer (shared encoding)

## Ports

- **5000**: Web interface and MJPEG stream
- **8554**: RTSP stream
- **8888**: WebRTC (future use)
- **8889**: HLS (future use)

## Troubleshooting

### RTSP Stream Not Working

1. Check if MediaMTX container is running:
   ```bash
   docker compose ps
   ```

2. Check MediaMTX logs:
   ```bash
   docker compose logs mediamtx
   ```

3. Verify RTSP stream is active:
   ```bash
   curl http://localhost:5000/api/stream/rtsp/status
   ```

4. Start RTSP stream if not active:
   ```bash
   curl -X POST http://localhost:5000/api/stream/rtsp/start
   ```

### Camera Errors on Page Reload

This should be fixed with the new implementation. The camera now properly handles:
- Multiple concurrent viewers
- Page reloads
- Simultaneous MJPEG and RTSP streaming
- Simultaneous viewing and recording

If you still experience issues:
1. Check the camera is not being used by another application
2. Verify camera permissions in Docker (`/dev/video0`)
3. Check application logs: `docker compose logs webcam-recorder`

## Security Notes

When deploying in production:
- Use HTTPS for the web interface
- Use RTSPS (RTSP over TLS) for encrypted streaming
- Implement authentication/authorization
- Consider rate limiting for the video feed endpoint
- Use a reverse proxy (nginx) for better performance
- Restrict access to RTSP port (8554) via firewall rules
