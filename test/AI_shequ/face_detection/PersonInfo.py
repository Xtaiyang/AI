import time
from enum import Enum


class State(Enum):
    staff = 1
    visitor = 2
    stranger = 3
    error = 4



class PersonInfo:
    life_time = 2000   # 存活时长（单位：毫秒）
    def __init__(self, name="None", state=State.error, birthday=time.time()):
        self.name = name
        self.state = state
        self.birthday = birthday

    def is_alive(self):
        alive = False
        time_difference = time.time() - self.birthday
        # print(f'is_alive : time_difference: {time_difference}')
        if time_difference < PersonInfo.life_time:
            alive = True
        return alive

