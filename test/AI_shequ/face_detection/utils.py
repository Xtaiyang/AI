import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import base64
from enum import Enum
from pathlib import Path






def convert_image_to_base64(image):
    # 将图片格式转为base64
    ret2, buffer = cv2.imencode('.jpg', image)
    base64_string = base64.b64encode(buffer)
    return base64_string


def put_Chinese_text_into_frame(frame, text, position, text_color=(0, 255, 0), text_size=30):
    if (isinstance(frame, np.ndarray)):  # 判断是否OpenCV图片类型
        frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(frame)
    # 字体的格式    
    # current_run_time_path = os.getcwd()
    font_file_name = "simsun.ttc"
    # dir_path = Path(os.path.realpath(__file__)).parent
    dir_path = Path('.', 'face_detection')
    font_path = Path.joinpath(dir_path, font_file_name)        
    fontStyle = ImageFont.truetype(
                    str(font_path),
                    text_size,
                    encoding="utf-8")
    # 绘制文本
    draw.text(position, text, text_color, font=fontStyle)
    # 转换回OpenCV格式
    frame = cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR)
    return frame


if __name__ == '__main__':

    cap = cv2.VideoCapture(0)
    while True:
        ret,frame = cap.read()
        # 展示图片
        frame = put_Chinese_text_into_frame(frame, "文本测试", (123, 123), (0, 255, 0), 30)
        cv2.imshow('capture', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    #释放对象和销毁窗口
    cap.release()
    cv2.destroyAllWindows()