import cv2
import numpy as np

from record_mp4 import process_video


def flip(frame):
    """图像翻转"""
    return cv2.flip(frame, 0)


net = cv2.dnn.readNetFromTensorflow(
    'model/opencv_face_detector_uint8.pb',
    'model/opencv_face_detector.pbtxt'
)  # TensorFlow模型


def face_detect(frame):
    """人脸检测"""
    frame = frame.copy()
    height, width, channel = frame.shape  # 高、宽、通道数
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300),
                                 (104.0, 177.0, 123.0))  # 调整大小并降低光照的影响
    net.setInput(blob)  # 设置输入
    detections = net.forward()  # 检测结果
    faces = detections[0, 0]  # 人脸结果
    for face in faces:
        confidence = face[2]  # 置信度
        if confidence > 0.5:  # 置信度阈值设为0.5
            box = face[3:7] * np.array([width, height, width, height])  # 人脸矩形框坐标
            pt1 = int(box[0]), int(box[1])  # 左上角坐标
            pt2 = int(box[2]), int(box[3])  # 右下角坐标
            cv2.rectangle(frame, pt1, pt2, (0, 255, 0), thickness=2)  # 画出人脸矩形框

            text = '{:.2f}%'.format(confidence * 100)  # 置信度文本
            startX, startY = pt1
            y = startY - 10 if startY - 10 > 10 else startY + 10
            org = (startX, y)  # 文本的左下角坐标
            cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), thickness=2)  # 画出置信度
    return frame


if __name__ == '__main__':
    process_video('test.mp4', func=face_detect, verbose=2)