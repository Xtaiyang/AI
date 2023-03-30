import os
import time
import cv2
import numpy
from pathlib import Path
from .PersonInfo import PersonInfo, State
from .HardWareControl import HardwareControl
from face_detection.FacesList import FacesList
from client.search_face_image_client import FaceImageSearch
from .utils import put_Chinese_text_into_frame

STAY_TIME = 5       # 在屏幕前超过 STAY_TIME 秒钟视为有访问需求。时间过短视为路过。单位：秒
FACE_RATIO = 0.8    # 在单位时间（STAY_TIME）内 超过 FACE_RATIO 比例的帧有人脸，表示确实有访问需求
face_list = FacesList(stay_time=STAY_TIME)
face_image_search = FaceImageSearch()
hardware_control = HardwareControl()


# 当存在多张人脸时，获取最大脸
def get_max_face(faces):
    face_max = faces[0]
    for (x, y, w, h) in faces:
        if w * h > face_max[2] * face_max[3]:
            face_max = (x, y, w, h)
    return face_max


def find_faces(frame_org):
    # current_run_time_path = os.getcwd()
    casc_xml_file_name = "haarcascade_frontalface_default.xml"
    # dir_path = Path(os.path.realpath(__file__)).parent
    dir_path = Path('.', 'face_detection')
    casc_path = Path.joinpath(dir_path, casc_xml_file_name)
    # opencv中人脸检测相关设置
    face_cascade = cv2.CascadeClassifier(str(casc_path))
    # 灰度化，检测人脸不可使用resize后的图，因此使用原始frame
    gray = cv2.cvtColor(frame_org, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(200, 200),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
    return faces


# 检测人脸
def face_detect_one_frame(frame_org):
    # 处理的结果
    frame_result = frame_org
    face_img = None  # 如果有人脸则返回人脸的截图，如果没有人脸则返回 None
    # 从图片中发现所有人脸
    faces = find_faces(frame_org)
    # 当检测到人脸时
    if len(faces) > 0:
        # 计数器，累计人脸数量
        # tags_num += 1

        # 获得最大面积的人脸
        face_max = get_max_face(faces)
        (x, y, w, h) = face_max
        x1, y1, x2, y2 = x, y, x + w, y + h
        # 图像区域必须为int类型
        ratio = 1  # 放大系数，默认为1
        (x1, y1, x2, y2) = numpy.dot([x1, y1, x2, y2], ratio).astype(int)
        # 截取脸
        face_img = frame_org[y1:y2, x1:x2, :]
        # cv2.imwrite("test_face.jpg", face_img) #测试用

        frame_result = cv2.rectangle(frame_org, (x1, y1), (x2, y2), (166, 40, 15), 3)
    return frame_result, face_img


def append_and_maintain_list(face_list, face_img):
    # 人脸图片和当前时刻信息加入队列
    face_list.put_face_image(face_img)
    # 裁剪队列。保留距离现在 n秒 内的元素
    face_list.crop_list()


def put_person_name_into_frame(frame, person_info):
    frame_result = frame
    # frame, text, position, textColor = (0, 255, 0), textSize = 30)
    if person_info.state != State.error:
        text = person_info.name
        position = (0, 0)
        text_color = (0, 255, 0)
        if person_info.state is State.staff or person_info.state is State.visitor:
            text_color = (0, 0, 255)     # 蓝色
        elif person_info.state is State.stranger:  # 陌生人
            text_color = (0, 255, 0)     # 绿色
        else:
            text_color = (255, 0, 0)     # 红色
        frame_result = put_Chinese_text_into_frame(frame, text, position, text_color=text_color)
    return frame_result


def send_request_callback(response_json, person_info):
    if response_json is None:  # 说明是网络错误
        person_info.name = '-网 络 错 误-'
        person_info.state = State.error   # 错误
        hardware_control.close_door()  # 关门
    elif response_json['success']:
        person_info.name = response_json['user_id']
        person_info.state = State.staff  # 员工
        hardware_control.open_door(auto_close_door=True)  # 开门
    else:
        person_info.name = '人员未注册'
        person_info.state = State.stranger  # 陌生人
        hardware_control.close_door()  # 关门


def face_detect_video(video_stream):
    """
    构造一个生成器。每一个元素是是一帧。对每一帧做处理
    :param video_stream:
    :return:
    """
    person_info = None
    hadrware_control = HardwareControl()

    for frame_org in video_stream:
        # 检测人脸是否存在，如果存在截取出面积最大的人脸
        frame, face_img = face_detect_one_frame(frame_org)
        # 把人脸加入队列，维持队列的长度为 2秒内的
        # append_and_maintain_list(face_list, face_img)
        # 人脸图片和当前时刻信息加入队列
        face_list.put_face_image(face_img)

        # 列表是否足够长，即采集时间足够长
        enough_long = face_list.is_enough_long()
        if enough_long:
            # 裁剪队列。保留距离现在 n秒 内的元素
            face_list.crop_list()
            # 收集连续 STAY_TIME秒 钟内的所有帧，如果其中超过 FACE_RATIO 有人脸，那么该人脸为待核验人脸
            ratio = face_list.compute_face_ratio()
            # 检查当前队列中人脸占比是否到阈值
            # 如果达到阈值，则返回当前人脸图片并且清空队列，用该人脸照片进行人脸比对搜索
            # 如果没有达到阈值，则什么都不做
            # print(f'len(face_list.list):{len(face_list.list)}')
            # print(f'ratio:{ratio}')

            if ratio > FACE_RATIO:
                last_face_img = face_list.get_last_face_image()
                face_list.clear()
                # print(f'len(face_list.list):{len(face_list.list)}')
                person_info = PersonInfo()

                # 调用人脸比对
                face_image_search.send_request(last_face_img,
                                               callback_function=send_request_callback,
                                               person_info=person_info)
        # 检查用户信息，如果符合条件，则在图像中合成人名
        if person_info is not None and person_info.is_alive():
            frame = put_person_name_into_frame(frame, person_info)
        yield frame


#### 测试用
def dealwith_frame(frame, counter):
    cv2.putText(frame, f"test {str(counter)}", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 0), 2)
    return frame