import time

from .base_camera import BaseCamera
import cv2


class Camera(BaseCamera):
    # 摄像头的id，第一个摄像摄像头编号为0，第二个摄像头编号为1，以此类推
    video_source_id = 0
    camera = None

    def __init__(self, video_source_id=0):
        Camera.video_source_id = video_source_id
        print(f'创建摄像头对象。摄像头编号为：{Camera.video_source_id}')
        BaseCamera.__init__(self)

    def __del__(self):
        """
        析构函数。释放资源
        :return:
        """
        if Camera.camera is not None:
            Camera.camera.release()

    def frames(self):
        '''
        这个函数必须是一个 生成器。吐出的是每一个帧。
        :return:
        '''
        print('真正开始从摄像头获取帧')
        if self.camera is None:
            print(f"开启摄像头。开启的编号为：{self.video_source_id}")
            self.camera = cv2.VideoCapture(self.video_source_id)
        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera.')
        while True:
            # read current frame
            ret, frame_original = self.camera.read()
            if ret is False:
                print('摄像头出错了！！！！！')
                # raise RuntimeError('摄像头出错了！！！！！')
                time.sleep(0.1)
                continue
            if frame_original is None:
                print('frame 是空的')
                time.sleep(0.1)
                continue
            # encode as a jpeg image and return it
            yield frame_original
