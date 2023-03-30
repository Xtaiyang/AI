
import json
import socket
import time
import urllib
import urllib.request
import urllib.parse
from enum import Enum
from threading import Thread
# from .utils import door_control


# from .utils import convert_image_to_base64
# from face_detection.PersonInfo import PersonInfo

IP = '192.168.2.206'    # 人脸闸机 nodeMCU 的IP地址
# IP = '192.168.2.206'    # 车牌闸机 nodeMCU 的IP地址
PORT = 80               # nodeMCU 的端口号



class DoorState(Enum):
    open = 0
    close = 1


import serial
def door_control(msg='1'):   #msg就是 0 和 1
    # msg:0表示开，1表示关
    #port = "COM3"
    port = '/dev/ttyAMA0'
    ser = serial.Serial(port, 115200, timeout=1)      #port=None,  串口号   timeout=None, 超时等待时间   baudrate=9600,  波特率
    time.sleep(2)
    ser.write(msg.encode())
    # COM6和115200要改，9600



class Method(Enum):
    network = 1
    usb = 2

class NodeMCUControl:
    def __init__(self, method=Method.network):
        self.method = method
        self.ip = IP
        self.port = PORT

    def __build_request(self, path):
        # 构造POST请求参数
        url_string = f'http://{IP}:{PORT}{path}'
        # print(url_string)
        request = urllib.request.Request(url=url_string)
        return request

    def __send_request(self, control_flag):
        """
        通过网络方式控制
        :param control_flag:
        :return:
        """

        path = '/close'
        if control_flag == 'open':
            path = '/open'
        elif control_flag == 'close':
            path = '/close'
        else:
            print(f'控制字符串出错了:{control_flag}')

        result_json = None
        request = self.__build_request(path)
        try:
            response = urllib.request.urlopen(request, timeout=5)
        except (urllib.request.URLError, socket.timeout) as e:
            # 捕获网络异常
            # print("服务器错误")
            # print(e)
            result_json = None
        else:
            result = response.read()
            # 将二进制 json 转为 utf-8 的字符串，进而转为 dict
            result_json = json.loads(str(result, encoding='utf-8'))
            # print("服务器返回结果为：")
            # print(result)
        finally:
            # print("访问服务器结束")
            return result_json

    def __usb_control(self, control_flag):
        """
        通过 USB 控制
        :param control_flag:
        :return:
        """
        result_json = json.dumps({"result":"success"})
        if control_flag == 'open':
            # usb 开门
            door_control('0')
            # pass
        elif control_flag == 'close':
            # usb 关门
            door_control('1')
            # pass
        else:
            print(f'控制字符串出错了:{control_flag}')
        return result_json

    def control(self, control_flag):
        result_json = json.dumps({"result":"success"})
        if self.method == Method.network:
            result_json = self.__send_request(control_flag)
        elif self.method == Method.usb:
            result_json = self.__usb_control(control_flag)
        else:
            print(f'硬件控制方式出错了：{self.method}')
        return result_json


class HardwareControl:
    def __init__(self):
        """
        根据不同场景初始化不同的控制
        """
        self.time_interval_between_open_and_close = 10   # 单位：秒
        self.node_MCU_control = NodeMCUControl(Method.network)
        # self.node_MCU_control = NodeMCUControl(Method.usb)
        print(f'创建硬件控制对象。控制方式为：{self.node_MCU_control.method}')



    def open_door(self, auto_close_door=True):
        print('向 NodeMCU 发送指令：开门')
        control_flag = 'open'
        result_json = self.node_MCU_control.control(control_flag)
        # 如果需要自动关门，那么 self.time_interval_between_open_and_close 秒后自动关门
        if auto_close_door is True:
            td = Thread(target=self.__auto_close_door)
            td.start()

    def close_door(self):
        print('向 NodeMCU 发送指令：关门')
        control_flag = 'close'
        result_json = self.node_MCU_control.control(control_flag)

    def __auto_close_door(self):
        time.sleep(self.time_interval_between_open_and_close)
        self.close_door()


if __name__ == '__main__':
    h = HardwareControl()
    h.open_door(auto_close_door=True)
    # h.close_door()
