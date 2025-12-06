# Streaming Options

This application provides webcam streaming via MJPEG (Motion JPEG) over HTTP, which is natively supported by most web browsers without requiring additional plugins.

## Built-in MJPEG Stream

The default streaming method is MJPEG over HTTP at the `/video_feed` endpoint:

- **URL**: `http://localhost:5000/video_feed`
- **Protocol**: HTTP multipart/x-mixed-replace
- **Format**: JPEG frames
- **Compatibility**: All modern browsers, VLC, ffmpeg

### Accessing the Stream

#### Web Browser
Simply navigate to `http://localhost:5000` to view the stream in the web interface.

#### VLC Media Player
1. Open VLC
2. Go to Media → Open Network Stream
3. Enter: `http://localhost:5000/video_feed`
4. Click Play

#### ffmpeg
```bash
ffplay http://localhost:5000/video_feed
```

#### curl (save frames)
```bash
# Save a single frame
curl http://localhost:5000/video_feed --output frame.jpg --max-time 1
```

## Alternative Streaming Protocols

If you need other streaming protocols (RTSP, HLS, WebRTC), you can extend the application:

### RTSP (Real Time Streaming Protocol)
For RTSP streaming, you would need to integrate a streaming server like:
- **GStreamer** with RTSP server
- **FFmpeg** with RTSP output
- **MediaMTX** (formerly rtsp-simple-server)

Example integration would involve:
1. Installing the streaming server
2. Piping frames from OpenCV to the server
3. Configuring the RTSP endpoint

### HLS (HTTP Live Streaming)
For HLS streaming (better for mobile devices):
1. Use FFmpeg to segment video into .ts files
2. Generate .m3u8 playlist
3. Serve via Flask static files or CDN

### WebRTC
For low-latency real-time streaming:
1. Integrate aiortc or similar WebRTC library
2. Implement signaling server
3. Add JavaScript client for WebRTC peer connection

## Current Implementation Benefits

The MJPEG approach was chosen for this implementation because:

- ✅ **Simple**: No additional streaming servers required
- ✅ **Compatible**: Works in all browsers and media players
- ✅ **Low Latency**: Direct HTTP stream without buffering
- ✅ **Easy Integration**: Native browser support with `<img>` tags
- ✅ **VLC Compatible**: Can be viewed in VLC as mentioned in requirements

## Performance Considerations

- MJPEG bandwidth usage is higher than H.264/H.265
- For production use with many viewers, consider HLS or RTSP
- Frame rate and resolution are configurable via environment variables
- The stream is multicast - multiple viewers share the same frames

## Security Notes

When deploying in production:
- Use HTTPS for encrypted streaming
- Implement authentication/authorization
- Consider rate limiting for the video feed endpoint
- Use a reverse proxy (nginx) for better performance
