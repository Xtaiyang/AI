import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import base64


def convert_image_to_base64(image):
    # 将图片格式转为base64
    ret2, buffer = cv2.imencode('.jpg', image)
    base64_string = base64.b64encode(buffer)
    return base64_string

