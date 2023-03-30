from flask import Flask, render_template, Response

import cv2
app = Flask(__name__)
app.video_stream = None
print(f"app.video_stream: {app.video_stream}")

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    if app.video_stream is None:
        raise RuntimeError("没有正确设置视频流")
    else:
        video_stream = app.video_stream
        
    return Response(video_stream,  # 生成器
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
