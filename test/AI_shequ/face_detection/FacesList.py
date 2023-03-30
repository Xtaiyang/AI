import time


class FrameTime:
    def __init__(self, face_image=None, time=time.time()):
        self.face_image = face_image
        self.time = time

    def copy(self):
        new_frametime = FrameTime()
        new_frametime.face_image = self.face_image.copy()
        new_frametime.time = self.face_image.copy()
        return new_frametime


class FacesList:
    def __init__(self, stay_time=2):
        self.list = []
        self.stay_time = stay_time

    def is_enough_long(self):
        """
        列表长度是不是足够长。判别标准就是列表中第一帧距离测试时刻超过了 self.stay_time
        :return:
        """
        result = False
        first_element = self.list[0]
        current_time = time.time()
        time_difference = current_time - first_element.time
        if time_difference >= self.stay_time:
            result = True
        return result


    def put_face_image(self, face_image):
        frame_time = FrameTime(face_image, time.time())
        self.list.append(frame_time)

    def get_last_face_image(self):
        lenth = len(self.list)
        face_image_result = None
        for index in reversed(range(lenth)):
            temp_face_image = self.list[index].face_image
            if temp_face_image is not None:
                face_image_result = temp_face_image
                break
        return face_image_result

    def crop_list(self):
        """
        裁剪list，只保留距离现在时刻 stay_time秒 内的元素
        :param stay_time:观测时长。例如，只保留 2秒内 的人脸信息
        :return: 新的 list
        """
        new_list = []
        current_time = time.time()
        for temp_frame_time in self.list:
            time_difference = current_time - temp_frame_time.time
            # print(f'time_difference: {time_difference}; stay_time: {stay_time}')
            if time_difference < self.stay_time:
                new_list.append(temp_frame_time)
        self.list = new_list
        return self.list

    def compute_face_ratio(self):
        """
        计算队列中真正的人脸的比例。
        :return:
        """
        face_ratio = 0
        face_image_counter = 0
        for temp_frame_time in self.list:
            if temp_frame_time.face_image is not None:
                face_image_counter += 1
        face_ratio = face_image_counter / len(self.list)
        return face_ratio

    def clear(self):
        self.list.clear()



































