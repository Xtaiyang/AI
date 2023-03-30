
import serial
from enum import Enum

class DoorState(Enum):
    open = 0
    close = 1

def door_control(msg=1):   #msg就是 0 和 1
    # msg:0表示开，1表示关
    port = "COM3"
    ser = serial.Serial(port, 115200, timeout=5)      #port=None,  串口号   timeout=None, 超时等待时间   baudrate=9600,  波特率
    ser.write(msg.encode())
    # COM6和115200要改，9600


# 开门
door_control(0)


