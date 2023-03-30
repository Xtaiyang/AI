import time

import cv2
import numpy
from camera.Camera import Camera
from window.window import Window
from face_detection.main_logic import face_detect_video
from flask_web_video_server.local_video_web_server import LocalWebVideoServer


if __name__ == '__main__':
    # 初始化摄像头
    camera_id = 0
    camera = Camera(camera_id)

    # 获取摄像头的视频流
    video_stream = camera.get_video_stream()

    # 对视频流做处理
    video_stream = face_detect_video(video_stream)

    # 本地窗口显示视频流
    window = Window()
    video_stream = window.play_video(video_stream)
    
    # 服务器远程显示视频
    web_server = LocalWebVideoServer()
    web_server.start_server(video_stream=video_stream)

