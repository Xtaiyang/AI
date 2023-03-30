import cv2




class Window():
    """
    获得每一帧图像后，在本地开启 OpenCV 窗口
    """
    def __init__(self, name="video", width=1024, height=600, location_x=0, location_y=0):
        self.name = name
        self.width = width
        self.height = height
        self.location_x = location_x
        self.location_y = location_y
        cv2.namedWindow(self.name)
        cv2.moveWindow(self.name, self.location_x, self.location_y)

    def __del__(self):
        """销毁当前对象的窗口"""
        # self.close_window()
        if cv2.getWindowProperty(self.name, cv2.WND_PROP_VISIBLE) > 0: #检查窗口状态
            self.close_window()

    def __show_one_frame(self, frame, frame_key_wait_time=1):
        """
        显示一帧画面，默认一帧画面的时长为 1 毫秒
        :param frame:一帧画面
        :param frame_key_wait_time:默认为 1 毫秒
        :return key:用户输入的键盘值
        """
        frame = cv2.resize(frame, dsize=(self.width, self.height), fx=1, fy=1, interpolation=cv2.INTER_LINEAR)
        cv2.imshow(self.name, frame)
        key = cv2.waitKey(frame_key_wait_time)   # 等待用户键盘输入时间内，画面静止。单位为毫秒数。0表示无限等待
        return key

    def close_window(self):
        """
        关闭窗口
        """
        cv2.destroyWindow(self.name)

    def play_picture(self, frame):
        """
        显示一张图片。按下'q'键或者‘esc’键后窗口关闭
        :param frame:显示的图片
        :return:
        """
        key = self.__show_one_frame(frame, 0)  # 等待键盘输入。0表示无限等待
        if key & 0xFF == ord('q') or key == 27:
            self.close_window()

    def play_video(self, frame_generator):
        """
        从生成器中读取每一帧，显示在窗口中。按下'q'键或者‘esc’键后窗口关闭
        :param frame_generator: 必须是生成器。每一个元素都是一帧
        :return:
        """
        for one_frame in frame_generator:
            key = self.__show_one_frame(one_frame, frame_key_wait_time=1) #1 ms
            if key & 0xFF == ord('q') or key == 27:
                self.close_window()
                break
            yield one_frame




if __name__ == "__main__":
    def test_play_picture():
        window = Window()
        frame = cv2.imread("./test_del.jpg")
        window.play_picture(frame)
    # test_play_picture()


    def test_play_video():
        window = Window()

        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        def camera_video():
            while True:
                # read current frame
                _, frame_original = camera.read()
                # encode as a jpeg image and return it
                yield frame_original

        window.play_video(camera_video())

    test_play_video()

