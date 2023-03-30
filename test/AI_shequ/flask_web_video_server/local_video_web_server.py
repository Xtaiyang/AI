import cv2


class LocalWebVideoServer:
    """
    对外提供基于 web 的视频流。
    视频的查看方式：
    1. 开启浏览器。访问 该服务器的 ip 端口号为 5000
    2. 视频流。访问 {IP地址}:5000/video_feed
    """

    @staticmethod
    def __frame_to_message(video_stream):
        """Video streaming generator function."""
        for frame in video_stream:
            frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
            http_message_content = b'--frame\r\n' \
                                   b'Content-Type: image/jpeg\r\n\r\n' \
                                   + frame_bytes \
                                   + b'\r\n'
            yield http_message_content

    def __init__(self, port=5000):
        from .app import app
        self.app = app
        self.port = port

    def start_server(self, video_stream=None):
        print(f"视频流服务器启动。端口号 {self.port}")
        port = self.port
        if video_stream is None:
            raise RuntimeError("视频服务器，没有接收到视频流")

        video_stream = LocalWebVideoServer.__frame_to_message(video_stream)
        self.app.video_stream = video_stream
        self.app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
