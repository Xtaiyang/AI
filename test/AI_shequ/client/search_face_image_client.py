import json
import socket
from threading import Thread
import urllib
import urllib.request
import urllib.parse
from .utils import convert_image_to_base64
from face_detection.PersonInfo import PersonInfo

IP = '192.168.2.105'
PORT = '7000'
PATH = '/api/web/external/recognizeFace'


class FaceImageSearch:
    def __init__(self):
        self.ip = IP
        self.port = PORT
        self.path = PATH
        self.params = {'image': None,
                       "image_type": "BASE64",
                       "group_id_list": "tests",
                       "quality_control": "LOW",
                       "liveness_control": "NONE"
                       }

    def __build_request(self, face_base64):
        # 构造POST请求参数
        url_string = f'http://{IP}:{PORT}{PATH}'
        self.params['image'] = face_base64
        params = self.params
        params = urllib.parse.urlencode(params).encode("utf-8")
        request = urllib.request.Request(url=url_string, data=params)
        request.add_header('Content-Type', 'application/json')
        return request

    def __send_http_message_thread(self, request, callback_function, person_info):
        result_json = None
        try:
            response = urllib.request.urlopen(request, timeout=5)
        except urllib.request.URLError as e:
            # 捕获网络异常
            # print("**** 服务器错误 ****")
            print(e)
            result_json = None
        except socket.timeout as e:
            # 捕获网络异常
            # print("**** 服务器错误----超时 ****")
            print(e)
            result_json = None
        else:
            result = response.read()
            # 将二进制 json 转为 utf-8 的字符串，进而转为 dict
            result_json = json.loads(str(result, encoding='utf-8'))
            # print("服务器返回结果为：")
            print(result_json)
        finally:
            print("访问服务器结束，调用回调函数")
            callback_function(result_json, person_info)


    def send_request(self, face_image, callback_function=None, person_info=None):
        face_base64 = convert_image_to_base64(face_image)
        request = self.__build_request(face_base64)

        td = Thread(target=self.__send_http_message_thread, args=(request, callback_function, person_info))
        td.start()
